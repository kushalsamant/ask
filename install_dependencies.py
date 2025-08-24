#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Installation Script
Detects hardware and installs appropriate dependencies for CPU/GPU image generation
Enhanced with comprehensive error handling, validation, and user experience
"""

import subprocess
import sys
import platform
import os
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('install_dependencies.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class InstallationError(Exception):
    """Custom exception for installation errors"""
    pass

class SystemValidator:
    """System validation and requirements checking"""
    
    @staticmethod
    def check_python_version():
        """Check if Python version is compatible"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            raise InstallationError(f"Python 3.8+ required, found {version.major}.{version.minor}")
        logger.info(f" Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    
    @staticmethod
    def check_disk_space():
        """Check available disk space"""
        try:
            import shutil
            total, used, free = shutil.disk_usage('.')
            free_gb = free // (1024**3)
            if free_gb < 5:  # Require at least 5GB
                raise InstallationError(f"Insufficient disk space: {free_gb}GB available, 5GB required")
            logger.info(f" Available disk space: {free_gb}GB")
            return True
        except Exception as e:
            logger.warning(f" Could not check disk space: {e}")
            return True
    
    @staticmethod
    def check_network_connectivity():
        """Check network connectivity"""
        try:
            import urllib.request
            urllib.request.urlopen('https://pypi.org', timeout=10)
            logger.info(" Network connectivity confirmed")
            return True
        except Exception as e:
            logger.warning(f" Network connectivity check failed: {e}")
            return False
    
    @staticmethod
    def check_virtual_environment():
        """Check if running in virtual environment"""
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        if in_venv:
            logger.info(" Running in virtual environment")
        else:
            logger.warning(" Not running in virtual environment (recommended)")
        return in_venv

def check_cuda_available():
    """Check if CUDA is available on the system"""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False

def get_cuda_version():
    """Get CUDA version if available"""
    try:
        import torch
        if torch.cuda.is_available():
            return torch.version.cuda
        return None
    except ImportError:
        return None

def install_pytorch_with_cuda():
    """Install PyTorch with CUDA support"""
    logger.info(" Detecting CUDA version...")
    
    # Try to detect CUDA version from system
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            # Parse CUDA version from nvidia-smi output
            for line in result.stdout.split('\n'):
                if 'CUDA Version:' in line:
                    cuda_version = line.split('CUDA Version:')[1].strip()
                    logger.info(f" Detected CUDA version: {cuda_version}")
                    
                    # Map CUDA version to PyTorch index
                    if '12.' in cuda_version:
                        return "cu121"
                    elif '11.8' in cuda_version:
                        return "cu118"
                    elif '11.7' in cuda_version:
                        return "cu117"
                    elif '11.6' in cuda_version:
                        return "cu116"
                    else:
                        return "cu118"  # Default to cu118
    except subprocess.TimeoutExpired:
        logger.warning(" nvidia-smi command timed out")
    except Exception as e:
        logger.warning(f" Could not detect CUDA version: {e}")
    
    logger.info(" Could not detect CUDA version, using default cu118")
    return "cu118"

def install_package_with_retry(package_cmd, max_retries=3):
    """Install package with retry logic"""
    for attempt in range(max_retries):
        try:
            logger.info(f" Installing package (attempt {attempt + 1}/{max_retries})...")
            result = subprocess.run(package_cmd.split(), capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info(" Package installed successfully")
                return True
            else:
                logger.warning(f" Installation attempt {attempt + 1} failed: {result.stderr}")
                if attempt < max_retries - 1:
                    time.sleep(5)  # Wait before retry
                    
        except subprocess.TimeoutExpired:
            logger.warning(f" Installation attempt {attempt + 1} timed out")
            if attempt < max_retries - 1:
                time.sleep(5)
        except Exception as e:
            logger.warning(f" Installation attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
    
    return False

def install_dependencies():
    """Install all dependencies with appropriate PyTorch version"""
    logger.info(" Smart Installation for Image Generation")
    logger.info("=" * 60)
    
    # System validation
    try:
        SystemValidator.check_python_version()
        SystemValidator.check_disk_space()
        SystemValidator.check_network_connectivity()
        SystemValidator.check_virtual_environment()
    except InstallationError as e:
        logger.error(f" System validation failed: {e}")
        return False
    
    # Check if CUDA is available
    cuda_available = check_cuda_available()
    
    if cuda_available:
        logger.info(" CUDA detected - Installing GPU-optimized PyTorch")
        cuda_version = get_cuda_version()
        if cuda_version:
            logger.info(f" CUDA version: {cuda_version}")
        
        # Install PyTorch with CUDA
        pytorch_index = install_pytorch_with_cuda()
        pytorch_cmd = f"pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/{pytorch_index}"
        
        logger.info(f" Installing PyTorch with {pytorch_index}...")
        if not install_package_with_retry(pytorch_cmd):
            logger.error(" Failed to install PyTorch with CUDA")
            logger.info(" Falling back to CPU-only PyTorch...")
            pytorch_cmd = "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"
            if not install_package_with_retry(pytorch_cmd):
                logger.error(" Failed to install PyTorch")
                return False
    else:
        logger.info(" No CUDA detected - Installing CPU-only PyTorch")
        pytorch_cmd = "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"
        
        logger.info(" Installing PyTorch for CPU...")
        if not install_package_with_retry(pytorch_cmd):
            logger.error(" Failed to install PyTorch")
            return False
    
    # Install other dependencies from requirements.txt
    logger.info(" Installing other dependencies...")
    requirements_cmd = f"{sys.executable} -m pip install -r requirements.txt"
    if not install_package_with_retry(requirements_cmd):
        logger.error(" Failed to install dependencies from requirements.txt")
        return False
    
    logger.info(" All dependencies installed successfully")
    return True

def verify_installation():
    """Verify that the installation was successful"""
    logger.info("\n Verifying installation...")
    
    verification_results = []
    
    try:
        import torch
        logger.info(f" PyTorch: {torch.__version__}")
        verification_results.append(("PyTorch", True, torch.__version__))
        
        if torch.cuda.is_available():
            logger.info(f" CUDA Available: {torch.cuda.get_device_name(0)}")
            logger.info(f" CUDA Version: {torch.version.cuda}")
            verification_results.append(("CUDA", True, torch.version.cuda))
        else:
            logger.info(" CPU-only PyTorch installed")
            verification_results.append(("CUDA", False, "CPU-only"))
        
        import diffusers
        logger.info(f" Diffusers: {diffusers.__version__}")
        verification_results.append(("Diffusers", True, diffusers.__version__))
        
        import transformers
        logger.info(f" Transformers: {transformers.__version__}")
        verification_results.append(("Transformers", True, transformers.__version__))
        
        import accelerate
        logger.info(f" Accelerate: {accelerate.__version__}")
        verification_results.append(("Accelerate", True, accelerate.__version__))
        
        try:
            import xformers
            logger.info(f" XFormers: {xformers.__version__}")
            verification_results.append(("XFormers", True, xformers.__version__))
        except ImportError:
            logger.info(" XFormers not installed (optional)")
            verification_results.append(("XFormers", False, "Not installed"))
        
        # Save verification report
        report = {
            "timestamp": datetime.now().isoformat(),
            "verification_results": verification_results,
            "success": all(result[1] for result in verification_results if result[0] != "XFormers")
        }
        
        with open('installation_verification.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("\n Installation verification successful!")
        logger.info(" Verification report saved to installation_verification.json")
        return True
        
    except ImportError as e:
        logger.error(f" Import error: {e}")
        return False

def cleanup_failed_installation():
    """Cleanup after failed installation"""
    logger.info("🧹 Cleaning up failed installation...")
    try:
        # Remove any partially installed packages
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "torch", "torchvision", "torchaudio"], 
                      capture_output=True)
        logger.info(" Cleanup completed")
    except Exception as e:
        logger.warning(f" Cleanup failed: {e}")

def main():
    """Main installation function"""
    logger.info("🧠 Smart Image Generation Dependencies Installer")
    logger.info("=" * 70)
    
    start_time = time.time()
    
    try:
        # Install dependencies
        success = install_dependencies()
        
        if success:
            # Verify installation
            verify_success = verify_installation()
            
            if verify_success:
                elapsed_time = time.time() - start_time
                logger.info(f"\n⏱ Installation completed in {elapsed_time:.1f} seconds")
                
                logger.info("\n Next steps:")
                logger.info("   1. Set GPU_IMAGE_GENERATION_ENABLED=true in ask.env (if you have GPU)")
                logger.info("   2. Set CPU_IMAGE_GENERATION_ENABLED=true in ask.env (for CPU fallback)")
                logger.info("   3. Run: python test_image_generation.py")
                logger.info("   4. Check install_dependencies.log for detailed logs")
                logger.info("   5. Check installation_verification.json for verification report")
                
                return 0
            else:
                logger.error("\n Installation verification failed")
                cleanup_failed_installation()
                return 1
        else:
            logger.error("\n Installation failed")
            cleanup_failed_installation()
            return 1
            
    except KeyboardInterrupt:
        logger.error("\n Installation interrupted by user")
        cleanup_failed_installation()
        return 1
    except Exception as e:
        logger.error(f"\n Unexpected error: {e}")
        cleanup_failed_installation()
        return 1

if __name__ == "__main__":
    sys.exit(main())
