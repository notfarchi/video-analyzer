import os
import subprocess
import time
from moviepy.editor import VideoFileClip
from faster_whisper import WhisperModel
from google.cloud import aiplatform
from vertexai import generative_models
from vertexai.generative_models import GenerativeModel, Part, Image

# ----------- CONFIGURAÇÃO -----------

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials/key.json"
PROJECT_ID = "video-biomundo"
LOCATION = "us-central1"
aiplatform.init(project=PROJECT_ID, location=LOCATION)

# ----------- FASTER WHISPER -----------

def has_audio_stream(video_path):
    result = subprocess.run(
        ["ffprobe", "-i", video_path, "-show_streams", "-select_streams", "a", "-loglevel", "error"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return bool(result.stdout.strip())

def extract_audio(video_path, audio_path):
    command = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audio_path
    ]
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def transcribe_audio_faster_whisper(audio_path, model_size="medium", language="pt"):
    model = WhisperModel(model_size, compute_type="auto")
    segments, _ = model.transcribe(audio_path, language=language, word_timestamps=True)
    words = []
    for segment in segments:
        for word in segment.words:
            words.append({"start": word.start, "end": word.end, "word": word.word})
    return words

# ----------- EXTRAÇÃO DE FRAMES -----------

def extract_frames(video_path, output_dir, interval=5):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vf", f"fps=1/{interval}",
        os.path.join(output_dir, "frame_%05d.jpg"),
        "-hide_banner", "-loglevel", "error"
    ]
    subprocess.run(cmd, check=True)

# ----------- GEMINI 2.0 FLASH (MULTIMODAL) -----------

class GeminiVisualAnalyzer:
    def __init__(self):
        self.model = GenerativeModel("gemini-2.0-flash")

    def analyze_image(self, image_path):
        image_part = Part.from_image(Image.load_from_file(image_path))
        prompt = "Descreva a cena da imagem de forma detalhada em português."
        response = self.model.generate_content([
            prompt,
            image_part
        ])
        return response.text.strip() if hasattr(response, "text") else "Sem descrição visual detectada"

# ----------- FORMATAÇÃO E PIPELINE -----------

def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02}:{m:02}:{s:02}"

def process_video(video_path, output_txt, interval=5, model_size="medium", language="pt", sleep_seconds=15):
    # 1. Extrai frames
    frames_dir = "frames_" + os.path.splitext(os.path.basename(video_path))[0]
    extract_frames(video_path, frames_dir, interval=interval)
    frame_files = sorted([os.path.join(frames_dir, f) for f in os.listdir(frames_dir) if f.endswith(".jpg")])

    # 2. Extrai e transcreve áudio
    audio_path = "audio_tmp.wav"
    if not has_audio_stream(video_path):
        print("O vídeo não contém faixa de áudio. Pulando transcrição.")
        words = []
    else:
        extract_audio(video_path, audio_path)
        words = transcribe_audio_faster_whisper(audio_path, model_size=model_size, language=language)

    # 3. Descrição visual com Gemini 2.0 Flash (com throttle)
    analyzer = GeminiVisualAnalyzer()
    captions = []
    for i, frame in enumerate(frame_files):
        print(f"Processando frame {i+1}/{len(frame_files)}: {frame}")
        caption = analyzer.analyze_image(frame)
        captions.append(caption)
        print(f"Descrição: {caption}")
        if i < len(frame_files) - 1:
            time.sleep(sleep_seconds)  # Evita burst de quota

    # 4. Organiza transcrição por intervalo (palavras que cruzam o bloco também entram)
    narration_by_interval = []
    for idx in range(len(frame_files)):
        ini = idx * interval
        fim = (idx + 1) * interval
        narration = " ".join([
            w["word"] for w in words
            if (w["start"] < fim and w["end"] > ini)
        ])
        narration_by_interval.append(narration if narration else "Sem fala detectada")

    # 5. Gera o .txt
    with open(output_txt, "w", encoding="utf-8") as f:
        for idx, (caption, narration) in enumerate(zip(captions, narration_by_interval), 1):
            ini = (idx) * interval
            fim = (idx + 1) * interval
            f.write(f"SCENE {idx}\n")
            f.write(f"TIME: {format_time(ini)} - {format_time(fim)}\n")
            f.write(f"[Visual: {caption}]\n")
            f.write(f"Narrador: {narration}\n\n")
    print(f"Arquivo '{output_txt}' gerado com sucesso.")

    # Limpeza opcional
    if os.path.exists(audio_path):
        os.remove(audio_path)
    for f in frame_files:
        os.remove(f)
    os.rmdir(frames_dir)

# ----------- USO -----------

if __name__ == "__main__":
    video_path = "videos/video1biomundo.mp4"  # Troque para o vídeo desejado
    output_txt = "video1biomundo_resultado.txt"
    process_video(video_path, output_txt, interval=5, model_size="medium", language="pt", sleep_seconds=15)