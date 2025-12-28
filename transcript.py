from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from urllib.parse import urlparse, parse_qs
from transformers import pipeline

# Load summarizer (you can use "t5-small" or "facebook/bart-large-cnn")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def extract_video_id(url):
    try:
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()

        # youtu.be short links
        if 'youtu.be' in netloc:
            return parsed.path.lstrip('/')

        # youtube.com variants
        if 'youtube.com' in netloc:
            # standard watch?v=VIDEO_ID
            q = parse_qs(parsed.query).get('v', [None])[0]
            if q:
                return q

            # paths like /shorts/VIDEO_ID or /embed/VIDEO_ID or /v/VIDEO_ID
            parts = [p for p in parsed.path.split('/') if p]
            if not parts:
                return None

            # common patterns: shorts, embed, v
            for i, p in enumerate(parts):
                if p in ('shorts', 'embed', 'v') and i + 1 < len(parts):
                    return parts[i + 1]

            # fallback: last path segment (helps with some shared URLs)
            return parts[-1]

        return None
    except Exception:
        return None


def get_transcript(video_id):
    try:
        yt_api = YouTubeTranscriptApi()
        transcript = yt_api.fetch(video_id)
        
        # FIX: Use entry.text instead of entry['text']
        transcript_text = "\n".join(entry.text for entry in transcript)

        return transcript_text

    except Exception as e:
        return f"Error: {str(e)}"
     
def split_text(text, max_tokens=1000):
    """Split text into smaller chunks for summarization."""
    sentences = text.split(". ")
    chunks = []
    chunk = ""

    for sentence in sentences:
        if len(chunk) + len(sentence) < max_tokens:
            chunk += sentence + ". "
        else:
            chunks.append(chunk.strip())
            chunk = sentence + ". "
    if chunk:
        chunks.append(chunk.strip())
    return chunks

def summarize_text(text):
    chunks = split_text(text, max_tokens=1000)
    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=150, min_length=1, do_sample=False)[0]['summary_text']
        summaries.append(summary)
    return "\n".join(summaries)

def main():
    video_url = input("Enter the YouTube video URL: ")
    video_id = extract_video_id(video_url)

    if not video_id:
        print("Invalid YouTube URL.")
        return

    transcript = get_transcript(video_id)

    # check for error
    if isinstance(transcript, str) and transcript.startswith("Error:"):
        print(transcript)
        return

    print("\nSummarizing transcript...\n")
    summary = summarize_text(transcript)
    print("\n--- Summary ---\n")
    print(summary)

    # Save full transcript and summary into a single file
    out_filename = f"{video_id}_transcript_and_summary.txt"
    with open(out_filename, "w", encoding="utf-8") as f:
        f.write("Full Transcript:\n")
        f.write(transcript)
        f.write("\n\n--- Summary ---\n")
        f.write(summary)

    print(f"\nTranscript and summary saved as {out_filename}")

if __name__ == "__main__":
    main()
