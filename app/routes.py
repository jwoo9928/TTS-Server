from flask import request, send_from_directory, send_file, stream_with_context, Response, url_for
from flask_restx import Api, Resource, reqparse
import os

def configure_routes(app, app_context):

    api = Api(app, version='1.0', title='TTS API', description='Swagger docs', doc="/docs")
    tts_api = api.namespace('tts', description='tts api')

    @tts_api.route('/tts_file', methods=['GET'])
    class tts(Resource):
        @tts_api.doc(params={
            'id': 'User ID',
            'text': 'Text to convert to speech',
            'language': 'Language code (default: en)',
            'model': 'Model to use (default: winter)'
        })
        def get(self):
            parser = reqparse.RequestParser()
            parser.add_argument('id', required=True, help="ID cannot be blank")
            parser.add_argument('text', required=True, help="Text cannot be blank")
            parser.add_argument('language', default='en', help="Default is English")
            parser.add_argument('model', default='winter', help="Default is winter")
            args = parser.parse_args()

            id = args['id']
            text = args['text']
            language = args['language']
            model = args['model']
            directory = os.path.dirname(__file__)
            print("directory", directory)
            buffer = app_context.predict_tts(id, text, language, f"./models/{model}.wav") 
            if buffer:
                try :
                    return Response(buffer.read(), mimetype="audio/wav")
                except Exception as e:
                    app.logger.error(f'Error: {str(e)}')
                    return {"error": str(e)}, 500
            else:
                app.logger.error('Conversion failed')
                return {"error": "Conversion failed"}, 500
        
    @tts_api.route('/tts_stream', methods=['GET'])
    class tts_stream(Resource):
        @tts_api.doc(params={
            'text': 'Text to convert to speech',
            'language': 'Language code (default: en)',
            'model': 'Model to use (default: winter)'
        })
        def get(self):
            parser = reqparse.RequestParser()
            parser.add_argument('text', required=True, help="Text cannot be blank")
            parser.add_argument('language', default='en', help="Default is English")
            parser.add_argument('model', default='winter', help="Default is winter")
            args = parser.parse_args()

            text = args['text']
            language = args['language']
            model = args['model']
            generator = app_context.streaming_tts(text, language, f"./models/{model}.wav") 
            if generator:
                return Response(stream_with_context(generator), mimetype='audio/x-wav')  # generator를 실행
            else:
                app.logger.error('Conversion failed')
                return {"error": "Conversion failed"}, 500

    @tts_api.route('/tts_stream_chunk_static', methods=['GET'])
    class tts_stream(Resource):
        @tts_api.doc(params={
            'text': 'Text to convert to speech',
            'language': 'Language code (default: en)',
            'model': 'Model to use (default: winter)',
        })
        def get(self):
            parser = reqparse.RequestParser()
            parser.add_argument('text', required=True, help="Text cannot be blank")
            parser.add_argument('language', default='en', help="Default is English")
            parser.add_argument('model', default='winter', help="Default is winter")
            args = parser.parse_args()

            text = args['text']
            language = args['language']
            model = args['model']
            generator = app_context.tts_stream_with_chunk_static(text, language, f"./models/{model}.wav") 
            if generator:
                return Response(stream_with_context(generator()), mimetype='audio/x-wav')  # generator를 실행
            else:
                app.logger.error('Conversion failed')
                return {"error": "Conversion failed"}, 500
            
    @tts_api.route('/tts_stream_chunk', methods=['GET'])
    class tts_stream(Resource):
        @tts_api.doc(params={
            'text': 'Text to convert to speech',
            'language': 'Language code (default: en)',
            'model': 'Model to use (default: winter)',
            'chunk_size': 'Chunk size (default: 20)'
        })
        def get(self):
            parser = reqparse.RequestParser()
            parser.add_argument('text', required=True, help="Text cannot be blank")
            parser.add_argument('language', default='en', help="Default is English")
            parser.add_argument('model', default='winter', help="Default is winter")
            parser.add_argument('chunk_size', default=20, help="Default is 20", type=int)
            args = parser.parse_args()

            text = args['text']
            language = args['language']
            model = args['model']
            chunk_size = args['chunk_size']
            generator = app_context.tts_stream_with_chunk(text, chunk_size, language, f"./models/{model}.wav") 
            if generator:
                return Response(stream_with_context(generator()), mimetype='audio/x-wav')  # generator를 실행
            else:
                app.logger.error('Conversion failed')
                return {"error": "Conversion failed"}, 500