class Request:
    def __init__(self, urls, file_paths, nsfw_threshold):
        self.urls = urls
        self.file_paths = file_paths
        self.nsfw_threshold = nsfw_threshold