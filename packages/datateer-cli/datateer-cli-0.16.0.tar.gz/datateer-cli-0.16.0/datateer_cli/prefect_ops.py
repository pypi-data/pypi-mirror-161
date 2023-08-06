import prefect

client = prefect.Client(
    api_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ0ZW5hbnRfaWQiOiI5MjdjMDU1OC0zNzQ5LTRjZmItYTI4Yi1jN2E2NGFhMWVlODYiLCJ1c2VyX2lkIjpudWxsLCJhcGlfdG9rZW5fc2NvcGUiOiJSVU5ORVIiLCJyb2xlIjoiUlVOTkVSIiwiaWF0IjoxNTcxMDg0ODQ4LCJleHAiOjQxMDI0NDQ4MDAsImp0aSI6ImI3ZGM3ZDVmLTU4ZWUtNDUxMy1iMDIzLWZlZDg2ZmQxMGZlMSIsImlzcyI6IlByZWZlY3QgQ2xvdWQiLCJhdWQiOiJQcmVmZWN0IENsb3VkIEFQSSIsInR5cCI6IkFQSSJ9.jOxFPB7Sl5gWnZVe_kSYAlS2j7A37R2MbseGA9EV5F7ma8s519ieAbkv43OrpD3rx__Z5iPOxD1g5smCm9niHBubGEmB2H5briaZbmTdymLpZKDvZjIvhp58GKW9JWxlc5RGU75bB5bnUMmB6Nt5Y7Trg_jxarEBVINTe86IlTnatOgTsULQYUDYGhLrCjHzXqXomBzuYC27Jxlv3t124z5gt7nhn1IS9VIaAGtTt73pco5caOvwwtyswZe9ZUvOdZTqIV1CADbBF-d-OkRGOWtdLstOZSg4bv4ScoJL69Q-GTE9M1ZggnqNj0X4wv78rmlgrIFq4Vq0XyWo22_xog"
)
client.save_api_token()


def create_client_project(client_code):
    print(f"Creating project for {client_code}")
    try:
        project_id = client.create_project(project_name=f"datateer-{client_code}")
        print(f"Created project datateer-{client_code}, id = {project_id}")
    except Exception:
        print(f"Project datateer-{client_code} already exists, skipping")


if __name__ == "__main__":
    create_client_project("hmn")
