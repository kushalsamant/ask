#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart Installation Script
Detects hardware and installs appropriate dependencies for CPU/GPU image generation
"""

import subprocess
import sys
import platform
import os

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
    print("🔍 Detecting CUDA version...")
    
    # Try to detect CUDA version from system
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            # Parse CUDA version from nvidia-smi output
            for line in result.stdout.split('\n'):
                if 'CUDA Version:' in line:
                    cuda_version = line.split('CUDA Version:')[1].strip()
                    print(f"✅ Detected CUDA version: {cuda_version}")
                    
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
    except:
        pass
    
    print("⚠️ Could not detect CUDA version, using default cu118")
    return "cu118"

def install_dependencies():
    """Install all dependencies with appropriate PyTorch version"""
    print("🚀 Smart Installation for Image Generation")
    print("=" * 50)
    
    # Check if CUDA is available
    cuda_available = check_cuda_available()
    
    if cuda_available:
        print("✅ CUDA detected - Installing GPU-optimized PyTorch")
        cuda_version = get_cuda_version()
        if cuda_version:
            print(f"✅ CUDA version: {cuda_version}")
        
        # Install PyTorch with CUDA
        pytorch_index = install_pytorch_with_cuda()
        pytorch_cmd = f"pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/{pytorch_index}"
        
        print(f"📦 Installing PyTorch with {pytorch_index}...")
        result = subprocess.run(pytorch_cmd.split(), capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PyTorch with CUDA installed successfully")
        else:
            print(f"❌ Failed to install PyTorch with CUDA: {result.stderr}")
            print("🔄 Falling back to CPU-only PyTorch...")
            pytorch_cmd = "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"
            subprocess.run(pytorch_cmd.split())
    else:
        print("💻 No CUDA detected - Installing CPU-only PyTorch")
        pytorch_cmd = "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"
        
        print("📦 Installing PyTorch for CPU...")
        result = subprocess.run(pytorch_cmd.split(), capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PyTorch for CPU installed successfully")
        else:
            print(f"❌ Failed to install PyTorch: {result.stderr}")
            return False
    
    # Install other dependencies from requirements.txt
    print("📦 Installing other dependencies...")
    result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ All dependencies installed successfully")
        return True
    else:
        print(f"❌ Failed to install dependencies: {result.stderr}")
        return False

def verify_installation():
    """Verify that the installation was successful"""
    print("\n🔍 Verifying installation...")
    
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
        
        if torch.cuda.is_available():
            print(f"✅ CUDA Available: {torch.cuda.get_device_name(0)}")
            print(f"✅ CUDA Version: {torch.version.cuda}")
        else:
            print("✅ CPU-only PyTorch installed")
        
        import diffusers
        print(f"✅ Diffusers: {diffusers.__version__}")
        
        import transformers
        print(f"✅ Transformers: {transformers.__version__}")
        
        import accelerate
        print(f"✅ Accelerate: {accelerate.__version__}")
        
        try:
            import xformers
            print(f"✅ XFormers: {xformers.__version__}")
        except ImportError:
            print("⚠️ XFormers not installed (optional)")
        
        print("\n🎉 Installation verification successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main installation function"""
    print("🧠 Smart Image Generation Dependencies Installer")
    print("=" * 60)
    
    # Install dependencies
    success = install_dependencies()
    
    if success:
        # Verify installation
        verify_installation()
        
        print("\n💡 Next steps:")
        print("   1. Set GPU_IMAGE_GENERATION_ENABLED=true in ask.env (if you have GPU)")
        print("   2. Set CPU_IMAGE_GENERATION_ENABLED=true in ask.env (for CPU fallback)")
        print("   3. Run: python test_image_generation.py")
        
    else:
        print("\n❌ Installation failed. Please check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
