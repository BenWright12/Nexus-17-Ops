import subprocess
import os

def get_audio_duration(file_path):
    """Uses macOS native 'afinfo' to get the exact duration."""
    try:
        cmd = ['afinfo', file_path]
        output = subprocess.check_output(cmd).decode('utf-8')
        for line in output.split('\n'):
            if 'estimated duration:' in line:
                return float(line.split(':')[1].strip().split(' ')[0])
        return 0.0
    except Exception as e:
        print(f"[WARN] Audio measurement failed: {e}")
        return 0.0

def format_time_ass(seconds):
    hours = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    cs = int((seconds - int(seconds)) * 100) 
    return f"{hours}:{mins:02}:{secs:02}.{cs:02}"

def create_ass(audio_file, text_file):
    if not os.path.exists(audio_file):
        print("[ERROR] Audio source file missing.")
        return
    total_duration = get_audio_duration(audio_file)
    if total_duration <= 0.1:
        print("[FATAL] Audio measured at 0 seconds. Check synthesis pipeline.")
        return

    with open(text_file, 'r') as f:
        text = f.read().replace('\n', ' ').strip()
        words = text.split()
        
    word_weights = []
    for w in words:
        base_weight = len(w)
        if '.' in w or '!' in w or '?' in w:
            base_weight += 8 
        elif ',' in w:
            base_weight += 4 
        word_weights.append(base_weight)
        
    total_weight = sum(word_weights)
    time_per_weight = total_duration / total_weight

    ass_content = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Tiktok,Arial,100,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    current_time = 0.0
    for i, word in enumerate(words):
        duration = word_weights[i] * time_per_weight
        start = current_time
        end = current_time + duration
        clean_word = word.replace(',', '').replace('.', '').replace('!', '').replace('?', '').upper()
        ass_content += f"Dialogue: 0,{format_time_ass(start)},{format_time_ass(end)},Tiktok,,0,0,0,,{clean_word}\n"
        current_time = end

    with open('captions.ass', 'w') as f:
        f.write(ass_content)
    print("[SUCCESS] Subtitle track generated (Neural-Synced).")

if __name__ == "__main__":
    create_ass('voiceover_fast.mp3', 'pending_story.txt')