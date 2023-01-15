<div align="center">
    <img src="resources/Logo.png" width="160" height="97">
</div>
<hr>
<p align="center">An image editor controlled with the hand</p>
<p align="center">
    <a href="https://www.youtube.com/watch?v=yOZVz0-dpwc">Watch Demo</a>
    ·
<a href="https://github.com/Mario-td/HandCamEditor/issues">Request Feature</a>
    ·
    <a href="https://github.com/Mario-td/HandCamEditor/issues">Report Bug</a>
</p>
<details open="open">
    <summary>Table of Contents</summary>
    <ol>
        <li>
            <a href="#about-the-project">About the Project</a>
            <ul>
                <li><a href="#technologies">Technologies</li>
            </ul>
        </li>
        <li>
            <a href="#getting-started">Getting Started</a>
            <ul>
                <li><a href="#prerequisites">Prerequisites</li>
                <li><a href="#run">Run</li>
            </ul>
        </li>
        <li><a href="#references">References</a></li>
        <li><a href="#license">License</a></li>
    </ol>
</details>

<h2 id="about-the-project">About the Project</h2>

<br>
<div align="center">
    <a href="https://www.youtube.com/watch?v=yOZVz0-dpwc"><img src="resources/App Screenshot.png" style="width: 75vw"></a>
</div>
<br>
<p>This image editor allows the user to control the cursor with their hand. The index finger leads the location of the cursor and the thumb contractions are used to click.</p> 
<p>Classical and AI processing methods can be applied to the images.</p> 
<h3 id="technologies">Technologies</h3>

<ul>
    <li><a href="https://www.python.org/downloads/release/python-3810">Python 3.8.10</a></li>
    <li><a href="https://pypi.org/project/PyQt5">PyQt5</a></li>
    <li><a href="https://github.com/opencv/">OpenCV 4.0.0 </a></li> 
    <li><a href="https://google.github.io/mediapipe">Mediapipe</a></li>
</ul>
    <h3 id="prerequisites">Prerequisites</h3>
    Download and install the aforementioned python version. It has not been tested with later versions

<br>
<h3 id="run">Run</h3>

Clone this repository

```shell
git clone https://github.com/Mario-td/HandCamEditor.git
cd HandCamEditor
```

Install the requiered packages

```shell
pip install -r requirements.txt
```

Run the application

```shell
python main.py
```

<h2 id="license">License</h2>

<p>Distributed under the MIT License. See <code>LICENSE</code> for more information.</p>
