"""
face_utils.py – Face-embedding helpers for TrashLock.

Uses facenet-pytorch with:
    - MTCNN for robust face detection, cropping, and alignment.
    - InceptionResnetV1 (pretrained on vggface2) producing 512-dimensional embeddings.

Key functions:
    get_embedding(image)    -> np.ndarray (512-d vector)
    cosine_distance(a, b)   -> float      (0 = identical, 2 = opposite)
    average_templates(list) -> np.ndarray (512-d averaged vector)
"""

import io
import numpy as np
from PIL import Image
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1

# Select CPU device (fast, lightweight, and requires no GPU drivers)
_device = torch.device("cpu")

# Initialise MTCNN face detector
# - image_size=160 matches InceptionResnetV1 input shape
# - keep_all=False returns the single most prominent detected face
_mtcnn = MTCNN(
    image_size=160,
    margin=0,
    min_face_size=20,
    keep_all=False,
    device=_device
)

# Initialise InceptionResnetV1 pretrained on VGGFace2
_resnet = InceptionResnetV1(pretrained="vggface2", device=_device).eval()


# ---------------------------------------------------------------------------
# Embedding extraction
# ---------------------------------------------------------------------------
def get_embedding(image) -> np.ndarray:
    """
    Accept raw image bytes (e.g. from st.camera_input) or a NumPy array
    (H, W, 3) (e.g. from LFW dataset), detect and align the face using MTCNN,
    and compute a 512-dimensional embedding using InceptionResnetV1.

    Returns:
        np.ndarray: 512-dimensional float32 feature vector.

    Raises:
        ValueError: If no face is detected in the image.
        TypeError:  If the input format is unsupported.
    """
    if isinstance(image, bytes):
        pil_img = Image.open(io.BytesIO(image)).convert("RGB")
    elif isinstance(image, np.ndarray):
        arr = image.copy()
        # Scale float [0.0, 1.0] images (such as scikit-learn LFW) to uint8 [0, 255]
        if arr.dtype != np.uint8 and arr.max() <= 1.0:
            arr = (arr * 255).astype(np.uint8)
        else:
            arr = arr.astype(np.uint8)
        pil_img = Image.fromarray(arr).convert("RGB")
    else:
        raise TypeError(f"Unsupported image type: {type(image)}. Expected bytes or np.ndarray.")

    # MTCNN returns a cropped face tensor (3, 160, 160) or None if no face detected
    face_tensor = _mtcnn(pil_img)
    if face_tensor is None:
        raise ValueError(
            "No face detected in the photo. "
            "Please make sure your face is clearly visible and well-lit."
        )

    # Compute 512-d embedding with InceptionResnetV1
    with torch.no_grad():
        embedding = _resnet(face_tensor.unsqueeze(0)).squeeze(0).cpu().numpy()

    return embedding.astype(np.float32)


# ---------------------------------------------------------------------------
# Distance & similarity
# ---------------------------------------------------------------------------
def cosine_distance(a, b) -> float:
    """
    Compute the cosine distance between two vectors.

        cosine_distance = 1 - cosine_similarity

    Returns a float in [0, 2]:
        0  → identical direction
        1  → orthogonal
        2  → opposite direction
    """
    a = np.array(a, dtype=np.float64)
    b = np.array(b, dtype=np.float64)

    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 1.0  # undefined – treat as "not similar"

    similarity = dot / (norm_a * norm_b)
    similarity = max(-1.0, min(1.0, float(similarity)))
    return float(1.0 - similarity)


# ---------------------------------------------------------------------------
# Template averaging
# ---------------------------------------------------------------------------
def average_templates(embeddings: list) -> np.ndarray:
    """
    Average several embeddings element-wise to produce a single template.

    Averaging multiple captures makes the template more robust to slight
    variations in pose, lighting, and expression.

    Returns:
        np.ndarray: 512-dimensional averaged template vector.
    """
    matrix = np.array(embeddings, dtype=np.float64)
    mean = matrix.mean(axis=0)
    return mean.astype(np.float32)
