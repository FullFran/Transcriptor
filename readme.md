<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <h1>Audio Transcription Project</h1>
    <p>This project automates the transcription of large audio files using Groq's API, handling files efficiently by splitting them into smaller chunks if they exceed a certain size limit.</p>

    <h2>Setup and Installation</h2>
    <p>Ensure you have the necessary dependencies installed:</p>
    <code>pip install groq wave python-dotenv</code>
    <p>Set up your environment variables in a <code>.env</code> file:</p>
    <code>API_KEY=your_groq_api_key_here</code>

    <h2>Usage</h2>
    <p>Run the script to process the audio files within the specified directory:</p>
    <code>python main.py</code>

    <h2>Dependencies</h2>
    <ul>
        <li>python-dotenv - Loads environment variables from a .env file.</li>
        <li>wave - Reads and writes WAV files.</li>
        <li>groq - Interacts with Groq's transcription API.</li>
    </ul>

    <h2>External Tools and Libraries</h2>
    <p>The following images show the libraries and APIs used in this project:</p>
    <img src="https://your_image_hosting/dotenv_logo.png" alt="dotenv library logo" />
    <img src="https://your_image_hosting/wave_library_image.png" alt="Wave library image" />
    <img src="https://your_image_hosting/groq_api_image.png" alt="Groq API logo" />


</body>
</html>
