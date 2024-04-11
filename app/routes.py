from flask import request, send_from_directory, send_file, current_app as app
from .xtts_api import initialize_model, gen_tts, predict_tts
import os

def configure_routes(app):

    @app.before_first_request
    def load_xtts_model():
        initialize_model()

    @app.route('/convert', methods=['POST'])
    def convert():
        data = request.json
        text = data.get('text')
        language = data.get('language', 'en')
        
        # Use the gen_tts function for asynchronous operation
        output_path = gen_tts(text, language)
        if output_path:
            return send_from_directory(directory=os.path.dirname(output_path), filename=os.path.basename(output_path), as_attachment=True)
        else:
            app.logger.error('Conversion failed')
            return {"error": "Conversion failed"}, 500
        
    @app.route('/tts', methods=['GET'])
    def tts():
        text = request.args.get('text')
        language = request.args.get('language', 'en')

        output_path = predict_tts(text, language, "../models/winter.wav") 
        if output_path:
            return send_from_directory(directory=os.path.dirname(output_path), filename=os.path.basename(output_path), as_attachment=True)
        else:
            app.logger.error('Conversion failed')
            return {"error": "Conversion failed"}, 500

    @app.route('/synthesize', methods=['POST'])
    def synthesize():
        data = request.json
        text = data['text']
        language = data.get('language', 'en')
        speaker_wav_path = '../models/winter.wav'

        output_path = predict_tts(text, language, speaker_wav_path)
        if output_path:
            return send_file(output_path, as_attachment=True)
        else:
            app.logger.error('Failed to synthesize')
            return {"error": "Failed to synthesize"}, 500
