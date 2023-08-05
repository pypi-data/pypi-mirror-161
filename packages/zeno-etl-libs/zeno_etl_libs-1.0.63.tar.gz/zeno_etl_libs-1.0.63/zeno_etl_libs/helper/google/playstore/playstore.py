import io


class Reviews:
    def __init__(self):
        pass

        # credentials = ServiceAccountCredentials.from_json_keyfile_name(
        #     '/Users/kuldeep/Downloads/playconsole-345511-8f3ba450d69b.json',
        #     scopes=['https://www.googleapis.com/auth/androidpublisher'])
        self.keyfile_dict = {
            "type": "service_account",
            "project_id": "playconsole-345511",
            "private_key_id": "8f3ba450d69bbe9694ae00f49f740912052694b8",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC0dsBllub9kOcE\nHoYA1uwFOxDQnNeuh52nPIogA+cwIWH4WfAALh2aVVf30Gf6rsjecUrCZz+8gCnd\nbHGOTbIIm+4F3XOXDRyyUIndEFTvr2/TxF2K+qW6PNSywzMHcWWKmxdJxyBrzqUi\ncTsXyH2S9WDOVelmhPMdjEvuPsU6h39zFUbITNw8YjhH1SrAZm0toOYZ/+D7RZJp\nwQApy8rxmi/6kiUNS/R9GNn0tuNE4PPT1xzpFn4stbqf2XWYtYVCb325jWmbAlj6\nfxYiWmGVlgeNlm8XiU0IVvOiCyj9WqPcG0ohOZ5OZxpf6lzkAfO+cYoBpOp7PCzN\nAKvcAB5TAgMBAAECggEASG/KNnzl5y38rLibzUZ3onnc+/+Yy2OAMpqoTsWCTN15\nd7iSD2BzXXmYP86VjhgOZMtQ2Muc18sSAuD+i8JADhiY6B3FwgHvXNvbGrLthPAE\nkRom+hw13ZWBQuf7Wad4vLQYGvMk3mEqA7Mzpw5A6XY5D1mIwC/pbhjceZsUi7Md\nS0YgX+d3WdMi6yCOT4ulOr5SBvtTt8KdQ2y3gMzRApP73PzdoygbQ/PhehTncf3I\nhSgZPnjU2612KFukWONSipuHzgWkaq20HmQEgVYyzohpntJFD6KQrtOL038yUEGm\n8sBhRkc1p9AQB21kjD/XNlH0koSBHwEVJM5KTWiP4QKBgQD5dEqBDKYuQC0HcKm9\nWuVyJPFzMGmbailTGEZb19HCsXh5jSSnH/BxeZ1HPW25d16vuH98x6pbbr1e85F5\nSJXYgU2hlWF34MVZTsTzf+uZ5aZa86fpSmoWcUVEu5L4Ygy7NxdjI0YJqZqWXNB5\npFQR6PeIRhdn5tAahxlwLXkYywKBgQC5MwSA+BYEQM+a2q2aWwh06LExbOlpckv7\nD3DD1f4kDMcqUlPpP0zaEnVPvknySO7JwHFkFLZRD0PWkM0RgNfrXkwXVVdXzx8E\nfyyl9ZKmPgaFx5L3/jY8M5IdYggaWJWtbvjsvyiKb2ACeEGI2HFCaK9nvCBOK4hj\nknUq8kBHmQKBgGuwLEmxsDvfMJE5rc005EB2elWD3NNe7SAWJqmXbdJi0uOGbwBG\n5YHXQnJyrl+WjKXHPCIeAAkgsVfARljZYPbqOx06Y61gt1Fqk9OasZbqcPpqnV40\n5b9yfrjBUR0xFtXrXolJvP6G3Vl0D/uzWSeyLsoBmDEej1AkanLm7pQpAoGBAIf7\n3u23u6rJz+Y7dUcmWpJFHX5WIxjq9MFWuA0DvsTHoSIBK13TveFNtlekOHWvea4o\nINpEnw3r8HrG/dxBR8mqBqMHZcey7GqH2sfNBi4M0ws93Ds9rKMNltb+WUbHDrg3\nCI4FWoYze0K0/CG4E4mYhlrb9riPHGlIa8Hp+KrZAoGBAI/m6ygHRllcJtl4BlJn\no4Py06mgQO2PT4lP2CEIVStF8mu4PY/oO7HHzDQe6EnvHRW0e8cKAepmSqa8kW4R\ndedaVm8SjGeU74mwGheWzQy7vsaDLafy3FDRAtFTvmE4kyyydVExWr2vAUi84TXM\nAuV9FqvKzQc5zcrT4xIEtRGu\n-----END PRIVATE KEY-----\n",
            "client_email": "playconsoleserviceacc@playconsole-345511.iam.gserviceaccount.com",
            "client_id": "103055631091973407668",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/playconsoleserviceacc%40playconsole-345511.iam.gserviceaccount.com"
        }

        self.package_name = "com.zenohealth.android"
        self.bucket_name = "pubsite_prod_rev_08705363625182098208"

    def get(self):
        from apiclient.discovery import build
        from httplib2 import Http
        from oauth2client.service_account import ServiceAccountCredentials

        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            keyfile_dict=self.keyfile_dict,
            scopes=['https://www.googleapis.com/auth/androidpublisher']
        )
        service = build('androidpublisher', 'v3', http=credentials.authorize(Http()))
        reviews_resource = service.reviews()
        reviews_page = reviews_resource.list(packageName=self.package_name, maxResults=100).execute()
        reviews_list = reviews_page["reviews"]

        infinite_loop_canary = 100
        while "tokenPagination" in reviews_page:
            reviews_page = reviews_resource.list(
                packageName=self.package_name,
                token=reviews_page["tokenPagination"]["nextPageToken"],
                maxResults=100).execute()
            reviews_list.extend(reviews_page["reviews"])
            infinite_loop_canary -= 1
            if infinite_loop_canary < 0:
                break

        for i in reviews_list:
            print((i['comments'][0]['userComment']['text'].encode("utf-8")))

        return reviews_list

    def download_blob_to_stream(self, source_blob_name):
        from google.cloud import storage
        from oauth2client.service_account import ServiceAccountCredentials
        """Downloads a blob to a stream or other file-like object."""

        # The ID of your GCS bucket
        # bucket_name = "your-bucket-name"

        # The ID of your GCS object (blob)
        # source_blob_name = "storage-object-name"

        # The stream or file (file-like object) to which the blob will be written

        file_obj = io.BytesIO()

        # credentials = service_account.Credentials.from_service_account_info(self.keyfile_dict)

        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            keyfile_dict=self.keyfile_dict,
        )
        storage_client = storage.Client(credentials=credentials)

        # storage_client = storage.Client.from_service_account_json('/Users/kuldeep/Downloads/playconsole-345511-8f3ba450d69b.json')

        # buckets = storage_client.list_buckets()
        # print(f"OK: ")
        # for bucket in buckets:
        #     print(bucket.name)
        #
        # blobs = storage_client.list_blobs(self.bucket_name)
        #
        # print("Blobs:")
        # for blob in blobs:
        #     print(blob.name)

        # print(f"buckets: {buckets}")
        bucket = storage_client.bucket(self.bucket_name)

        # Construct a client-side representation of a blob.
        # Note `Bucket.blob` differs from `Bucket.get_blob` in that it doesn't
        # retrieve metadata from Google Cloud Storage. As we don't use metadata in
        # this example, using `Bucket.blob` is preferred here.

        blob = bucket.blob(source_blob_name)
        blob.download_to_file(file_obj)
        #
        print(f"Downloaded blob {source_blob_name} to file-like object.")

        # return file_obj

        # Before reading from file_obj, remember to rewind with file_obj.seek(0).

    def get_all_review(self, count=100):
        """
        returns: latest reviews by count
        """
        from google_play_scraper import Sort, reviews

        result, continuation_token = reviews(
            self.package_name,
            lang='en',  # defaults to 'en'
            country='us',  # defaults to 'us'
            sort=Sort.NEWEST,  # defaults to Sort.NEWEST
            count=50  # batch size
        )

        # If you pass `continuation_token` as an argument to the reviews function at this point,
        # it will crawl the items after count review items.
        all_results = result
        while len(all_results) < count and result:
            print(f"continuation_token: {continuation_token}")
            result, continuation_token = reviews(
                self.package_name,
                continuation_token=continuation_token  # defaults to None(load from the beginning)
            )
            all_results += result

        return all_results
