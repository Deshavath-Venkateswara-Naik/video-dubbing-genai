import os
import subprocess
import logging
import sys

# Add Wav2Lip to sys.path
WAV2LIP_PATH = os.path.join(os.path.dirname(__file__), "lip_sync", "Wav2Lip")
if WAV2LIP_PATH not in sys.path:
    sys.path.append(WAV2LIP_PATH)

logger = logging.getLogger(__name__)

class LipSyncService:
    def __init__(self):
        self.wav2lip_dir = WAV2LIP_PATH
        self.checkpoint_path = os.path.join(
            self.wav2lip_dir, "checkpoints", "wav2lip.pth"
        )
        self.face_det_checkpoint = os.path.join(
            self.wav2lip_dir,
            "face_detection",
            "detection",
            "sfd",
            "s3fd.pth"
        )

        # Ensure checkpoint directory exists
        os.makedirs(os.path.dirname(self.checkpoint_path), exist_ok=True)

    def is_model_available(self):
        """Check if required checkpoints exist."""
        return (
            os.path.exists(self.checkpoint_path)
            and os.path.exists(self.face_det_checkpoint)
        )

    async def sync_lips(self, video_path, audio_path, output_path):
        """
        Runs Wav2Lip inference on the given video and audio.
        Uses CPU and optimized parameters.
        """
        # Convert to absolute paths to ensure Wav2Lip subprocess finds them
        video_path = os.path.abspath(video_path)
        audio_path = os.path.abspath(audio_path)
        output_path = os.path.abspath(output_path)
        if not self.is_model_available():
            logger.error(
                f"Wav2Lip or Face Detection checkpoint not found. "
                f"Expected at:\n{self.checkpoint_path}\n{self.face_det_checkpoint}"
            )
            return False

        logger.info(
            f"Starting LipSync for {video_path} using {audio_path}..."
        )

        python_exe = sys.executable
        inference_script = os.path.join(self.wav2lip_dir, "inference.py")

        command = [
            python_exe,
            inference_script,
            "--checkpoint_path",
            self.checkpoint_path,
            "--face",
            video_path,
            "--audio",
            audio_path,
            "--outfile",
            output_path,
            "--resize_factor",
            "2",              # Faster CPU processing
            "--wav2lip_batch_size",
            "8",              # Small batch for CPU
            "--pads",
            "0", "10", "0", "0"
        ]

        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.wav2lip_dir,
                text=True
            )

            if result.returncode == 0:
                logger.info("LipSync completed successfully.")
                return True
            else:
                logger.error(f"LipSync failed:\n{result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error during LipSync: {e}")
            return False