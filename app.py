import streamlit as st
from rembg import remove
from PIL import Image, UnidentifiedImageError
import tempfile
import os
import io

# Set up Streamlit app configuration
st.set_page_config(page_title="Image Processor", layout="centered")

# Load CSS
st.markdown("""
<style>
body {
    font-family: Arial, sans-serif;
    background-color: #f8f9fa;
    margin: 0;
    padding: 0;
}
.container {
    background: #ffffff;
    padding: 20px 40px;
    border-radius: 8px;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 600px;
    margin: auto;
}
h1 {
    color: #333;
    font-size: 24px;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# App Title
st.markdown("<div class='container'><h1>Image Background Replacement Tool</h1></div>", unsafe_allow_html=True)

# File upload widgets
foreground_file = st.file_uploader("Upload Foreground Image (JPEG/PNG)", type=["jpg", "jpeg", "png"])
background_file = st.file_uploader("Upload Background Image (JPEG/PNG)", type=["jpg", "jpeg", "png"])

# Helper function to process images
def process_images(foreground, background):
    try:
        # Open and convert images to RGBA
        fg_img = Image.open(foreground).convert("RGBA")
        bg_img = Image.open(background).convert("RGBA")

        # Resize images to manageable dimensions if too large
        max_size = 1024
        fg_img.thumbnail((max_size, max_size))

        # Process the foreground image to remove the background
        fg_byte_arr = io.BytesIO()
        fg_img.save(fg_byte_arr, format="PNG")
        processed_data = remove(fg_byte_arr.getvalue(), alpha_matting=True)
        processed_fg_img = Image.open(io.BytesIO(processed_data)).convert("RGBA")

        # Resize the background to match the dimensions of the processed foreground
        bg_img = bg_img.resize(processed_fg_img.size)

        # Composite images
        composite_img = Image.alpha_composite(bg_img, processed_fg_img)

        return composite_img
    except UnidentifiedImageError:
        st.error("Uploaded file is not a valid image. Please try again.")
        return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

    try:
        # Open and resize images
        fg_img = Image.open(foreground).convert("RGBA")
        bg_img = Image.open(background).convert("RGBA")

        # Resize to manageable dimensions if too large
        max_size = 1024
        fg_img.thumbnail((max_size, max_size))
        bg_img.thumbnail(fg_img.size)

        # Remove background
        fg_byte_arr = io.BytesIO()
        fg_img.save(fg_byte_arr, format="PNG")
        processed_data = remove(fg_byte_arr.getvalue(), alpha_matting=True)
        processed_fg_img = Image.open(io.BytesIO(processed_data)).convert("RGBA")

        # Composite images
        composite_img = Image.alpha_composite(bg_img, processed_fg_img)

        return composite_img
    except UnidentifiedImageError:
        st.error("Uploaded file is not a valid image. Please try again.")
        return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Process images and display results


# Process the images when both are uploaded
if foreground_file and background_file:
    with st.spinner("Processing images..."):
        try:
            # Load images and log dimensions
            foreground_img = Image.open(foreground_file).convert("RGBA")
            background_img = Image.open(background_file).convert("RGBA")

            st.write(f"Original Foreground Dimensions: {foreground_img.size}")
            st.write(f"Original Background Dimensions: {background_img.size}")

            # Resize images to manageable dimensions
            max_size = 1024
            foreground_img.thumbnail((max_size, max_size))
            st.write(f"Resized Foreground Dimensions: {foreground_img.size}")

            # Process the foreground image to remove the background
            temp_foreground = io.BytesIO()
            foreground_img.save(temp_foreground, format="PNG")
            processed_data = remove(temp_foreground.getvalue(), alpha_matting=True)
            processed_foreground = Image.open(io.BytesIO(processed_data)).convert("RGBA")
            st.write(f"Processed Foreground Dimensions: {processed_foreground.size}")

            # Resize the background to match the dimensions of the processed foreground
            background_resized = background_img.resize(processed_foreground.size)
            st.write(f"Resized Background Dimensions: {background_resized.size}")

            # Composite the foreground and background images
            output_img = Image.alpha_composite(background_resized, processed_foreground)

            # Display the result
            st.image(output_img, caption="Final Output Image", use_container_width=True)
            st.success("Image processing completed!")

            # Download button for the output image
            output_img_path = io.BytesIO()
            output_img.save(output_img_path, format="PNG")
            output_img_path.seek(0)
            st.download_button(
                label="Download Output Image",
                data=output_img_path,
                file_name="output.png",
                mime="image/png"
            )

        except UnidentifiedImageError:
            st.error("One of the uploaded files is not a valid image. Please try again.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
else:
    st.info("Please upload both foreground and background images to proceed.")

