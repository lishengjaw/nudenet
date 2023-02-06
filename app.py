from nudenet import NudeClassifier
from flask import Flask, request
from request import Request
import requests
import os
from constants import PORT_NUMBER, DEFAULT_NSFW_THRESHOLD

app = Flask(__name__)
path = os.path.dirname(os.path.abspath(__file__))
classifier = NudeClassifier()


@app.route('/detect_nsfw_images', methods=['POST'])
def detect_nsfw_images():
    try:
        request, error = read_request()
        if error:
            return write_error(error)
        detect_results = detect_images(request)
        return write_results(detect_results, request)
    except Exception as e:
        print('error: ' + str(e))
        return write_error('server error')


def read_request():
    urls = request.form.getlist('urls')
    if len(urls) == 0:
        return None, "no urls found with the 'urls' key"

    file_path_to_file_content = {}
    for index, url in enumerate(urls):
        response = requests.get(url)
        if response.status_code == 200:
            file_path_to_file_content[f'user_images/image_{index}.jpg'] = response.content
        else:
            return None, 'one or more urls are invalid'

    nsfw_threshold_str = request.form.get('nsfw_threshold')
    nsfw_threshold_float = DEFAULT_NSFW_THRESHOLD
    if nsfw_threshold_str:
        try:
            nsfw_threshold_float = float(nsfw_threshold_str)
            if nsfw_threshold_float < 0 or nsfw_threshold_float > 1:
                raise Exception
        except:
            return None, 'nsfw_threshold must be a value between 0 and 1 inclusive'

    for file_path, file_content in file_path_to_file_content.items():
        open(file_path, 'wb').write(file_content)

    return Request(urls, list(file_path_to_file_content.keys()), nsfw_threshold_float), ''


def detect_images(request):
    file_paths = request.file_paths
    detect_results = classifier.classify(file_paths)

    for file_path in file_paths:
        os.remove(file_path)

    return detect_results


def write_results(detect_results, request):
    nsfw_threshold = request.nsfw_threshold
    results = {'results': [], 'message': 'success',
               'nsfw_threshold': nsfw_threshold}
    index = 0

    for _, result in detect_results.items():
        results['results'].append({
            'url': request.urls[index],
            'unsafe_score': result['unsafe'],
            'safe_score': result['safe'],
            'is_nsfw': True if result['unsafe'] >= nsfw_threshold else False
        })
        index += 1
    return results


def write_error(error_message):
    return {'message': error_message}


if __name__ == '__main__':
    app.run()
