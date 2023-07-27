# Py-Tess-OCR
**Py-Tess-OCR** is a cutting-edge offline optical character recognition (OCR) software, designed to empower users with seamless text extraction capabilities. Developed on the powerful Tesseract OCR engine and integrated with Python and Tkinter module, Py-Tess-OCR brings forth a user-friendly Graphical User Interface (GUI) for effortless text recognition tasks.

<p align="center">
  <img width="500" src="https://github.com/HasithaSuneth/Py-Tess-OCR/assets/87106402/09c16379-c0ba-4bb9-bf70-fb2480a6b0df" alt="Block Diagram">
</p>

## Application Features:

1. **Versatile Input Format Support:** <br>
   The application offers seamless support for the most common image formats, including jpg, jpeg, png, gif, bmp, as well as PDF formats, allowing users to work with a wide range of input files.

2. **Efficient Directory Processing:** <br>
   Users can conveniently select a directory containing images and PDF files as input, streamlining the processing of multiple files. The application intelligently combines all outputs into a single file for easy management.

3. **Multilingual Text Recognition:** <br>
   The application excels in recognizing and processing text in various languages, thanks to its compatibility with the Tesseract OCR engine, which supports a diverse set of languages.

4. **Advanced OCR Functionality:** <br>
   Leveraging the powerful capabilities of the Tesseract OCR engine, the application incorporates advanced functionalities to ensure accurate and high-quality text extraction.

5. **Flexible Output Formats:** <br>
   Users have the freedom to generate output in multiple formats, including txt, doc, md, hocr, and tsv, catering to diverse use cases and preferences.

6. **Streamlined Clipboard Integration:** <br>
   With built-in support for direct output to the clipboard, users can efficiently copy and paste extracted text to other applications, eliminating the need for intermediate file storage.

The application's comprehensive features make it a reliable and efficient tool for text extraction, capable of handling various input formats and delivering output in user-preferred formats. By leveraging the capabilities of the Tesseract OCR engine, it ensures accurate text recognition and supports multiple languages, enhancing its usability for a wide range of users and scenarios. With an intuitive interface and seamless clipboard integration, the application aims to streamline the text extraction process and provide an exceptional user experience.

## Step-by-Step Guide to Using Py-Tess-OCR
1. **Input Selection:** <br>
Start by selecting either a single image/PDF file or a directory containing multiple images and PDF files. This provides the input for the text extraction process.

2. **Custom Output Naming (Optional):** <br>
If you prefer a specific output file name, you have the option to enter it. Otherwise, the application defaults to naming the output file as '_**output**_' with the appropriate file-type extension.

3. **Output Format Selection:** <br>
Choose the desired output file format from the provided drop-down menu. The default selection is the 'txt' format, but you have the flexibility to pick from various formats based on your needs.

4. **Language Selection:** <br>
Select the language/s associated with the input file/s. Py-Tess-OCR supports a diverse range of languages, ensuring accurate text recognition across different linguistic sources.

5. **Unlocking Advanced Functionalities:** <br>
For more sophisticated OCR tasks, click on the 'Advanced Option' button. Hover over each option to gain valuable insights into how they enhance the text extraction process.

6. **Generating the Output:** <br>
Once you have chosen your settings, click on the 'Generate' button to initiate the text extraction process. The output file will be generated and saved at the location of the original input file.

7. **Efficient Clipboard Integration:** <br>
Alternatively, if you prefer to copy the output details directly to the clipboard without generating a file, click on the 'Clipboard' icon. After receiving the successful message, paste the extracted content to the required location.

## Installation Guide:

**Windows System:** <br>
- For Windows systems, no installation process is needed. Users can simply extract the files and use the application as a portable application.

**Linux System:** <br>
1. **Install Tesseract OCR Engine:** <br>
Begin the Linux installation process by installing the Tesseract OCR engine. This can typically be accomplished using the package manager of your Linux distribution. For example:
```
sudo apt-get install tesseract-ocr
```
2. **Install Poppler Package:** <br>
Next, ensure you have the Poppler package installed on your system. Poppler is required to handle PDF files. Install it using your package manager, similar to the Tesseract installation:
```
sudo apt-get install poppler-utils
```
3. **Download and Extract Py-Tess-OCR Linux Edition:** <br>
Download the Py-Tess-OCR Linux edition package and extract its contents. Once extracted, the application can be used as a portable application.
```
wget https://github.com/HasithaSuneth/Py-Tess-OCR/releases/download/v1.0/Py-Tess-OCR.v1.0.Linux.zip
```

## Step-by-Step Guide to Adding New Languages to Py-Tess-OCR:

1. **Download the Required Language:** <br>
Begin by visiting Tesseract OCR's official GitHub page and accessing the desired language data. Utilize the provided links to download the required language file. Users have the option to select either optimized trained language data or best-trained language data based on their preferences and needs.
- [Language Data - Optimized](https://github.com/tesseract-ocr/tessdata)
- [Language Data - Best](https://github.com/tesseract-ocr/tessdata_best)
- [Language Keywords](https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html)

2. **Placement of Language Data:** <br>
After downloading the `'<language-name>.traindata'` file, navigate to the (`Tesseract/tessdata` | `Windows`) (`/usr/share/tesseract-ocr/5/tessdata/` | `Linux`) location. Place the downloaded language data file in this directory to ensure proper accessibility within the Py-Tess-OCR application.
```
# In Linux systems, the user may require to change the downloaded language file permission.
sudo chmod 644 /usr/share/tesseract-ocr/5/tessdata/<language-name>.traineddata
```
3. **Accessing the New Language:** <br>
With the language data successfully placed in the designated directory, the newly added language becomes readily accessible within the Py-Tess-OCR application. Users can now leverage this language option for enhanced multilingual text extraction capabilities.

## Download: <br>
- [Py-Tess-OCR (Windows)](https://github.com/HasithaSuneth/Py-Tess-OCR/releases/download/v1.0/Py-Tess-OCR.v1.0.Winx64.rar)
- [Py-Tess-OCR (Linux)](https://github.com/HasithaSuneth/Py-Tess-OCR/releases/download/v1.0/Py-Tess-OCR.v1.0.Linux.zip)
