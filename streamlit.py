import streamlit as st
import os
from PIL import Image
import time
import subprocess

fitmi_logo = Image.open("/content/AI-Model/LOGO_NO_BG_cropped.png")

def main():
    st.sidebar.image(fitmi_logo, width=200)
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select Page", ["Home", "Try Clothes"])

    if page == "Home":
        st.title("Welcome to FITMI")
        st.write("This is the homepage of FITMI app.")

    elif page == "Try Clothes":
        try_clothes_page()

def try_clothes_page():
    st.title("Try Clothes")
    col1, col2 = st.columns(2)
    col1.markdown('#### Category')
    category = col1.selectbox(
        'Select category',
        ('upper_body', 'lower_body', 'dresses'),
        index=None
    )
    col2.markdown('#### Gender')
    gender = col2.selectbox(
        'Select gender',
        ('male', 'female'),
        index=None
    )
    st.markdown('\n\n\n')
    st.markdown('\n\n\n')
    st.markdown('\n\n\n')
    st.markdown('\n\n\n')
    st.markdown('\n\n\n')

    if category and gender:
        col1, col2 = st.columns(2)

        # Cloth image
        col1.markdown('#### Cloth image')
        cloth_key = f"cloth_{category}_{gender}"
        option_cloth = col1.radio("Select option:", ("Upload image", "Capture from camera"), key=cloth_key)
        if option_cloth == "Upload image":
            uploaded_cloth = col1.file_uploader("Upload cloth image", type=["jpg", "jpeg", "png"])
        else:  # Capture from camera
            uploaded_cloth = col1.camera_input("Upload cloth image")
        # Person image
        col2.markdown('#### Person image')
        person_key = f"person_{category}_{gender}"
        option_person = col2.radio("Select option:", ("Upload image", "Capture from camera"), key=person_key)
        if option_person == "Upload image":
            uploaded_person = col2.file_uploader("Upload person image", type=["jpg", "jpeg", "png"])
        else:  # Capture from camera
            uploaded_person=col2.camera_input("Upload person image")

        if (option_cloth == "Upload image" and uploaded_cloth is None) or (option_person == "Upload image" and uploaded_person is None):
            st.warning("Please upload both cloth and person images to continue..")
        else:
            if uploaded_cloth is not None:
                if category == "upper_body":
                    cloth_saved_folder = "/content/AI-Model/datasets/vitonHDDataset/test/cloth/cloth_1.jpg"
                    clear_directory("/content/AI-Model/datasets/vitonHDDataset/test/cloth")
                elif category == "lower_body":
                    cloth_saved_folder = '/content/AI-Model/datasets/dresscodeDataset/lower_body/images/cloth_1.jpg'
                    clear_directory("/content/AI-Model/datasets/dresscodeDataset/lower_body/images")
                else:  # Assume category is "dresses"
                    cloth_saved_folder = '/content/AI-Model/datasets/dresscodeDataset/dresses/images/cloth_1.jpg'
                    clear_directory("/content/AI-Model/datasets/dresscodeDataset/dresses/images")

                cloth_image = Image.open(uploaded_cloth)
                cloth_image.save(cloth_saved_folder)
                col1.image(cloth_image, caption='Cloth Image', use_column_width=True)

            if uploaded_person is not None:
                if category == "upper_body":
                    person_saved_folder = "/content/AI-Model/datasets/vitonHDDataset/test/image/person_0.jpg"
                    clear_directory("/content/AI-Model/datasets/vitonHDDataset/test/image")
                elif category == "lower_body":
                    person_saved_folder = '/content/AI-Model/datasets/dresscodeDataset/lower_body/images/person_0.jpg'
                else:  # Assume category is "dresses"
                    person_saved_folder = '/content/AI-Model/datasets/dresscodeDataset/dresses/images/person_0.jpg'

                person_image = Image.open(uploaded_person)
                person_image.save(person_saved_folder)
                col2.image(person_image, caption='Person Image', use_column_width=True)

            if st.button('Generate'):
                # Add spinner
                with st.spinner('Please wait for the processing to finish, it may take few minutes ...'):
                    command = [
                        "python",
                        "/content/AI-Model/src/inference.py",
                        "--category",
                        category,
                        "--gender",
                        gender
                    ]
                    subprocess.run(command)
                    output_folder = ""
                    if category == "upper_body":
                        output_folder = "/content/AI-Model/datasets/vitonHDDataset/test/output/unpaired/upper_body"
                    elif category == "lower_body":
                        output_folder = '/content/AI-Model/datasets/dresscodeDataset/lower_body/output/unpaired/lower_body'
                    else:  # Assume category is "dresses"
                        output_folder = '/content/AI-Model/datasets/dresscodeDataset/dresses/output/unpaired/dresses'

                    output_ready = False

                    # if not output_ready:
                    #     st.write("Output images are not available yet. Please wait for the processing to finish.")
                    while not output_ready:
                        if os.path.exists(output_folder) and len(os.listdir(output_folder)) > 0:
                            output_ready = True
                        else:
                            time.sleep(1)

                    output_files = os.listdir(output_folder)
                    if output_files:
                        cols = st.columns([1, 2, 1])  # Create three columns
                        for output_file in output_files:
                            output_image = Image.open(os.path.join(output_folder, output_file))
                            cols[1].image(output_image, caption='Output Image', width=400)

                        recommendation_folder = ""
                        if category == "upper_body":
                            recommendation_folder = "/content/AI-Model/recommendationSystem/upper_body/output"
                        elif category == "lower_body":
                            recommendation_folder = '/content/AI-Model/recommendationSystem/lower_body/output'
                        else:  # Assume category is "dresses"
                            recommendation_folder = '/content/AI-Model/recommendationSystem/dresses/output'

                        display_images_in_columns(recommendation_folder, "Recommended Clothes")

                        complementary_folder = ""
                        if gender == "male":
                            complementary_folder = "/content/AI-Model/recommendationSystem/complementary/male/output"
                        else:
                            complementary_folder = "/content/AI-Model/recommendationSystem/complementary/female/output"

                        display_images_in_columns(complementary_folder, "Complementary Items")
                    else:
                        st.error('Please try again later.')
    else:
        st.warning("Please select both category and gender.")

def display_images_in_columns(folder_path, header_text, num_columns=5):
    st.header(header_text)
    files = os.listdir(folder_path)
    num_images = min(len(files), num_columns)
    cols = st.columns(num_images)
    for i in range(num_images):
        image_path = os.path.join(folder_path, files[i])
        image = Image.open(image_path)
        cols[i].image(image, caption=f'Image {i+1}', use_column_width=True)

def clear_directory(destination_dir):
    for file_name in os.listdir(destination_dir):
        file_path = os.path.join(destination_dir, file_name)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.remove(file_path)
        else:
            print(f"Skipped: {file_path} (Not a file or link)")

if __name__ == "__main__":
    main()
