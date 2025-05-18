import os
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import random
import sys

# Load environment variables from .env file
print("Loading environment variables from .env file...")
load_dotenv()

# Get credentials from environment variables
aws_access_key = os.getenv("DIGITAL_OCEAN_SPACES_ACCESS_KEY")
aws_secret_key = os.getenv("DIGITAL_OCEAN_SPACES_SECRET_KEY")
region = os.getenv(
    "DIGITAL_OCEAN_SPACES_REGION", "nyc3"
)  # Get region from env or use default
space_name = os.getenv(
    "DIGITAL_OCEAN_SPACE_NAME", "unstuck-goose"
)  # Default based on error message
endpoint_url = f"https://{region}.digitaloceanspaces.com"

# Print debug info (masking sensitive data)
print(f"Access Key: {'*' * 4}{aws_access_key[-4:] if aws_access_key else 'None'}")
print(f"Secret Key: {'*' * 4}{aws_secret_key[-4:] if aws_secret_key else 'None'}")
print(f"Region: {region}")
print(f"Space Name: {space_name}")
print(f"Endpoint URL: {endpoint_url}")

# Path to the test image
LOCAL_IMAGE_PATH = "test_screenshots/test_captcha.png"
REMOTE_IMAGE_PATH = f"uploads/test_captcha{random.randint(1,10000)}.png"


def upload_to_space(local_file, remote_file):
    """
    Upload a file to DigitalOcean Spaces

    Args:
        local_file (str): Path to the local file
        remote_file (str): Path in the Space where the file will be stored

    Returns:
        bool: True if upload was successful, False otherwise
    """
    try:
        # Initialize the S3 client for DigitalOcean Spaces
        s3 = boto3.client(
            "s3",
            region_name=region,
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
        )

        # Upload the file with public-read ACL to make it publicly accessible
        extra_args = {
            "ACL": "public-read",  # This makes the file publicly accessible
            "ContentType": "image/png",  # Set the appropriate content type
        }

        print(f"Uploading with public-read ACL...")
        s3.upload_file(local_file, space_name, remote_file, ExtraArgs=extra_args)
        print(f"Upload Successful: {local_file} -> {space_name}/{remote_file}")

        # Generate and print the public URL
        public_url = (
            f"https://{space_name}.{region}.digitaloceanspaces.com/{remote_file}"
        )
        print(f"Public URL: {public_url}")

        return True
    except FileNotFoundError:
        print(f"The file was not found: {local_file}")
        return False
    except NoCredentialsError:
        print("Credentials not available or invalid")
        return False
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False


def test_upload_image():
    """Test function to upload the test image to DigitalOcean Spaces"""
    print("Starting test: Upload image to DigitalOcean Spaces")

    # Validate environment variables
    if not aws_access_key or not aws_secret_key:
        print("ERROR: Missing required environment variables.")
        print(
            "Make sure DIGITAL_OCEAN_SPACES_ACCESS_KEY and DIGITAL_OCEAN_SPACES_SECRET_KEY are set in .env file"
        )
        return False

    # Validate the space name
    if space_name == "your-space-name":
        print(
            "WARNING: Using default space name. Set DIGITAL_OCEAN_SPACE_NAME in .env for production use."
        )

    # Validate the image file exists
    if not os.path.exists(LOCAL_IMAGE_PATH):
        print(f"ERROR: Test image not found at {LOCAL_IMAGE_PATH}")
        print("Make sure you're running this script from the mcp_server directory")
        return False

    # Upload the image
    result = upload_to_space(LOCAL_IMAGE_PATH, REMOTE_IMAGE_PATH)

    if result:
        print("Test PASSED: Image uploaded successfully")
    else:
        print("Test FAILED: Could not upload image")

    return result


if __name__ == "__main__":
    test_upload_image()
