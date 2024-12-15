import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Initialize the S3 client
s3_client = boto3.client('s3')

# Bucket name
BUCKET_NAME = 'myimages52'


def upload_file_to_s3(file_name, object_name=None):

    if object_name is None:
        object_name = file_name

    try:
        s3_client.upload_file(file_name, BUCKET_NAME, object_name)
        print(f"File '{file_name}' uploaded to '{BUCKET_NAME}/{object_name}'")
        return True
    except FileNotFoundError:
        print(f"The file '{file_name}' was not found.")
    except NoCredentialsError:
        print("Credentials not available.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return False


def download_file_from_s3(object_name, file_name=None):
    if file_name is None:
        file_name = object_name

    try:
        s3_client.download_file(BUCKET_NAME, object_name, file_name)
        print(f"File '{object_name}' downloaded from '{BUCKET_NAME}' to '{file_name}'")
        return True
    except FileNotFoundError:
        print(f"The file '{file_name}' could not be created.")
    except NoCredentialsError:
        print("Credentials not available.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return False


if __name__ == "__main__":
    """
    file_to_upload = 'test.txt'  # Replace with your file path
    upload_file_to_s3(file_to_upload)
    input("ol")
    s3_object_name = 'test.txt'  # Replace with the object name in S3
    download_file_from_s3(s3_object_name, 'downloaded_test.txt')
    """
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
    print(response['Contents'])
    print(type(response))
