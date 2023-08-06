import boto3
import librosa
import soundfile as sf
import requests

def upload_sample():
    """ Downsamples an audio file with librosa and uploads it to an S3 bucket."""    
    y, sr = librosa.load(librosa.ex('trumpet'), sr=22050)
    y_8k = librosa.resample(y, orig_sr=sr, target_sr=8000)
    sf.write('sample.wav', y_8k, 8000, 'PCM_24')
    s3 = boto3.client('s3')
    with open("sample.wav", "rb") as f:
        s3.upload_fileobj(f, "francois-aws-transcribe", "sample.wav")
    print("Success: Upload works")

def check_if_request_works():
    """ Try to ping non-existent link """    
    r = requests.get('https://www.google.co.za/')
    print("Success: Requests work")

