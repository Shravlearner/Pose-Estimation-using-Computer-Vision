# Pose-Based Re-Identification in Video Streams

## Description

This project presents a real-time system for person re-identification (Re-ID) in video streams using pose estimation. Traditional Re-ID methods often rely on appearance-based features, which can be unreliable under varying clothing and lighting conditions. Our system addresses these challenges by identifying individuals based on their unique postures, utilizing pose estimation to enhance accuracy.

Key features include:

- **Real-Time Processing**: Leveraging a pre-trained pose estimation model.
- **Pose-Based Features**: More robust identification, overcoming appearance-based limitations.
- **Client-Server Architecture**: Distributed video processing with intelligent frame selection.

Potential applications include video surveillance, activity monitoring, and scenarios requiring robust posture-based identification.

---

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Shravlearner/Pose-Estimation-using-Computer-Vision
   cd Pose-Estimation-using-Computer-Vision
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure the following prerequisites**:

   - Python 3.8+
   - TensorFlow
   - OpenCV
   - NumPy

---

## Usage

1. **Run the main script**:

   ```bash
   python main.py
   ```

2. **Provide video input**:
   The system supports live video feed from a camera or pre-recorded video files. Modify `config.py` to set the input source.

3. **Monitor outputs**:

   - Visualize detected poses and edges.
   - Identification results are logged to the console and stored in the output directory.

---

## Repository Structure

- **Core Files**:

  - `main.py`: Entry point of the system.
  - `modelImplementation.py`: Core implementation of pose estimation and feature extraction.
  - `client.py` & `server.py`: Client-server architecture components.
  - `SSIM` Variants (`clientNoSSIM.py`, `serverSSIM.py`): Optimize frame processing using Structural Similarity Index (SSIM).

- **Pre-trained Models**:

  - `lite-model_movenet_singlepose_lightning_3.tflite`
  - `lite-model_movenet_singlepose_lightning_tflite_int8_4.tflite`

- **Example Videos**:

  - Folder `videos/` contains sample video files for testing.

- **Documentation**:

  - `README.md`: Project documentation.

---

## Methodology

### System Architecture

- **Client-Side**:
  - Processes video frames to extract pose features using a pre-trained model.
  - Employs SSIM-based adaptive frame selection for efficiency.
- **Server-Side**:
  - Maintains a database of pose features.
  - Identifies individuals by comparing pose features using a similarity metric (e.g., Euclidean distance).

### Evaluation Metrics

- **Rank-1 Accuracy**: Measures correct identification at the top rank.
- **Mean Average Precision (mAP)**: Evaluates retrieval performance.
- **CMC Curve**: Displays the probability of correct identification across ranks.

---

## Results

- **Dataset**: Market-1501, CUHK03
- **Rank-1 Accuracy**: 78.2%
- **Mean Average Precision**: 62.5%
- **CMC Curve**: Achieved 85.4% accuracy within top 5 ranks.

---


