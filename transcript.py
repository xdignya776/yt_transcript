from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

def get_transcript(video_id):
    try:
        # Fetch the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Extract and join the transcript text into a single string
        transcript_text = "\n".join([entry['text'] for entry in transcript])

        return transcript_text

    except Exception as e:
        return f"Error: {str(e)}"

def main():
    # Input: YouTube video ID
    video_url = input("Enter the YouTube video URL: ")
    
    # Extract the video ID from the URL
    video_id = video_url.split("v=")[-1].split("&")[0]
    
    # Get the transcript
    transcript = get_transcript(video_id)
    
    if "Error" not in transcript:
        print("\nTranscript:\n")
        print(transcript)
    else:
        print(f"{transcript}")

if __name__ == "__main__":
    main()