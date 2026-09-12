import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify;

load_dotenv()
from getVideoDetails import getVideoDetails;
from sumTranscript import sumTranscript;
from chat import update_vector_store, ask_question, VectorStoreNotFoundError
from getChapters import generate_chapters

app = Flask(__name__);

@app.route('/')
def home():
    return "YouTube Summary API is working!";

@app.route('/api/get-video-details', methods=['POST'])
def videoData():
    data = request.get_json();
    video_url = data.get("video_url");

    if not video_url:
        return jsonify({"error": "Missing video_url"}), 400;

    try:
        result  = getVideoDetails(video_url);

        if "error" in result:
            return jsonify({"error": result["error"]}), 500;

        title = result["title"];
        transcript_text = result["transcript_text"];
        formatted_transcript = result["formatted_transcript"];

        summary = sumTranscript(transcript_text);
        chapters = generate_chapters(formatted_transcript);

        return jsonify({
                "title":title,
                "transcript":formatted_transcript,
                "chapter":chapters,
                "summary": summary
            });
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/update-vector-store', methods=['POST'])
def update_vector():
    data = request.get_json() or {}
    video_id = data.get("video_id")
    transcript_text = data.get("transcript_text")

    if not video_id:
        return jsonify({"error": "Missing video_id"}), 400
    if not transcript_text:
        return jsonify({"error": "Missing transcript_text"}), 400

    try:
        update_vector_store(str(video_id), transcript_text)
        return jsonify({"message": "Vector store updated successfully", "video_id": str(video_id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/api/chat', methods=['POST'])
def chat_with_video():
    data = request.get_json() or {}
    video_id = data.get("video_id")
    question = data.get("question")

    if not video_id:
        return jsonify({"error": "Missing video_id"}), 400
    if not question:
        return jsonify({"error": "Missing question"}), 400

    try:
        answer = ask_question(str(video_id), question)
        return jsonify({"answer": answer})
    except VectorStoreNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, port=port)