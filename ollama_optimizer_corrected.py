import psutil
import os
import subprocess
import sys
from typing import Dict, Any, List, Optional
from langchain_ollama import OllamaLLM

class OllamaOptimizer:
    """
    Advanced Ollama optimization class with full LangChain-Ollama integration.
    Handles system detection, parameter optimization, and GPU configuration.
    """

    def __init__(self, model_name: str = "deepseek-r1"):
        """Initialize the optimizer with system detection and configuration."""
        self.model_name = model_name
        
        # System information
        self.cpu_count = psutil.cpu_count()
        self.memory_gb = psutil.virtual_memory().total / (1024**3)
        self.has_gpu = self._check_gpu_availability()
        
        # LangChain-Ollama supported parameters only
        self.supported_params = {
            'model', 'temperature', 'top_p', 'top_k', 'num_predict', 
            'num_ctx', 'num_thread', 'repeat_penalty', 'repeat_last_n',
            'seed', 'stop', 'system', 'template', 'format', 'keep_alive',
            'mirostat', 'mirostat_eta', 'mirostat_tau', 'tfs_z'
        }
        
        print(f"🔍 System detected: {self.cpu_count} CPU cores, {self.memory_gb:.1f}GB RAM, GPU: {self.has_gpu}")

    def _check_gpu_availability(self) -> bool:
        """Enhanced GPU detection with multiple methods."""
        
        # Method 1: Check for nvidia-smi
        try:
            result = subprocess.run(['nvidia-smi'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            pass
        
        # Method 2: Check for torch CUDA
        try:
            import torch
            if torch.cuda.is_available():
                return True
        except ImportError:
            pass
        
        # Method 3: Check environment variables
        cuda_visible = os.environ.get('CUDA_VISIBLE_DEVICES')
        if cuda_visible and cuda_visible != '-1':
            return True
            
        return False

    def get_optimized_config(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Get optimized configuration based on system specs."""
        
        if model_name is None:
            model_name = self.model_name
            
        # Base configuration with LangChain-Ollama supported parameters
        config = {
            "model": model_name,
            "temperature": 0.5,  # Balanced for speed and quality
            "top_p": 0.9,        # Good balance for coherence
            "system": self._get_optimized_system_prompt()
        }

        # CPU optimization
        if self.cpu_count >= 16:
            config["num_thread"] = min(8, self.cpu_count - 2)  # Leave some cores for system
        elif self.cpu_count >= 8:
            config["num_thread"] = min(6, self.cpu_count - 2)
        else:
            config["num_thread"] = max(2, self.cpu_count - 1)

        # Memory optimization
        if self.memory_gb >= 32:
            config["num_ctx"] = 8192      # Large context for powerful systems
            config["num_predict"] = 1024  # Allow longer responses
        elif self.memory_gb >= 16:
            config["num_ctx"] = 4096      # Medium context
            config["num_predict"] = 512   # Moderate response length
        elif self.memory_gb >= 8:
            config["num_ctx"] = 2048      # Standard context
            config["num_predict"] = 256   # Shorter responses
        else:
            config["num_ctx"] = 1024      # Minimal context
            config["num_predict"] = 128   # Very short responses

        # Response optimization
        config["repeat_penalty"] = 1.1      # Reduce repetition
        config["repeat_last_n"] = 64        # Look back for repetitions
        config["keep_alive"] = "5m"         # Keep model loaded for 5 minutes

        # Speed optimization
        if self.has_gpu:
            config["temperature"] = 0.4      # Slightly lower for GPU speed
            config["top_k"] = 40            # Balanced sampling
        else:
            config["temperature"] = 0.5      # Higher for CPU creativity
            config["top_k"] = 20            # More focused sampling for CPU

        return config

    def _get_optimized_system_prompt(self) -> str:
        """Get optimized system prompt for performance."""
        return """You are JARVIS, an efficient AI assistant. Guidelines:
        1. Be concise and direct in responses
        2. Provide 1-2 sentences unless detail is requested
        3. Use clear, natural language
        4. Stay focused on the core question
        5. Avoid unnecessary elaboration"""

    def create_optimized_llm(self, model_name: Optional[str] = None) -> OllamaLLM:
        """Create optimized OllamaLLM instance using the configuration."""
        
        try:
            # Get optimized configuration
            config = self.get_optimized_config(model_name)
            
            # Remove system prompt from config and handle separately
            system_prompt = config.pop('system', '')
            
            # Validate parameters
            validated_config = self._validate_parameters(config)
            
            # Create LLM instance
            llm = OllamaLLM(**validated_config)
            
            print(f"✅ Created optimized LLM with {validated_config.get('num_thread', 'auto')} threads")
            return llm
            
        except Exception as e:
            print(f"❌ Error creating LLM: {e}")
            # Fallback to basic configuration
            return OllamaLLM(model=model_name or self.model_name)

    def _validate_parameters(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and filter parameters for LangChain-Ollama compatibility."""
        
        validated = {}
        
        for key, value in config.items():
            if key in self.supported_params:
                validated[key] = value
            else:
                print(f"⚠️  Skipping unsupported parameter: {key}")
        
        return validated

    def print_system_info(self) -> None:
        """Print detailed system information."""
        print("\n" + "="*50)
        print("🖥️  SYSTEM INFORMATION")
        print("="*50)
        print(f"CPU Cores: {self.cpu_count}")
        print(f"Memory: {self.memory_gb:.1f} GB")
        print(f"GPU Available: {self.has_gpu}")
        
        if self.has_gpu:
            try:
                result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    gpu_info = result.stdout.strip().split('\n')[0]
                    print(f"GPU Details: {gpu_info}")
            except:
                print("GPU Details: Available but cannot query")
        
        print("="*50)

    def get_performance_tips(self) -> List[str]:
        """Get performance optimization tips based on system specs."""
        tips = []

        # CPU-specific tips
        if self.cpu_count < 4:
            tips.append("⚠️  Consider upgrading to a CPU with 8+ cores for better performance")
        elif self.cpu_count >= 16:
            tips.append("✅ Excellent CPU for high-performance inference")

        # Memory-specific tips
        if self.memory_gb < 8:
            tips.append("⚠️  Consider adding more RAM (16GB+ recommended)")
        elif self.memory_gb >= 32:
            tips.append("✅ Excellent RAM for large models")

        # GPU-specific tips
        if not self.has_gpu:
            tips.append("💡 Consider using a GPU for 3-10x faster inference")
        else:
            tips.append("✅ GPU acceleration enabled")

        # General optimization tips
        tips.extend([
            "🔧 Close unnecessary applications to free system resources",
            "📊 Monitor ollama with 'ollama ps' to check GPU usage",
            "🎯 Use smaller models (7B vs 13B) for faster responses",
            "⚡ Adjust num_ctx lower (1024-2048) for speed-critical apps",
            "🔄 Use keep_alive parameter to avoid model reloading",
            "🧪 Experiment with temperature (0.3-0.7) for different creativity levels"
        ])

        return tips

    def optimize_for_speed(self) -> Dict[str, Any]:
        """Get configuration optimized specifically for speed."""
        speed_config = self.get_optimized_config()
        
        # Speed-focused adjustments
        speed_config.update({
            "temperature": 0.3,      # Lower for faster, more deterministic responses
            "top_k": 20,            # Smaller sampling space
            "top_p": 0.8,           # More focused sampling
            "num_predict": 128,     # Shorter responses
            "repeat_penalty": 1.05,  # Minimal repetition penalty
        })
        
        # Reduce context for speed if memory is limited
        if self.memory_gb < 16:
            speed_config["num_ctx"] = min(speed_config["num_ctx"], 1024)
            
        return speed_config

    def optimize_for_quality(self) -> Dict[str, Any]:
        """Get configuration optimized for response quality."""
        quality_config = self.get_optimized_config()
        
        # Quality-focused adjustments
        quality_config.update({
            "temperature": 0.6,      # Higher for more creative responses
            "top_k": 60,            # Larger sampling space
            "top_p": 0.95,          # Broader sampling
            "num_predict": 512,     # Longer responses allowed
            "repeat_penalty": 1.15,  # Stronger repetition penalty
        })
        
        # Increase context for quality if memory allows
        if self.memory_gb >= 16:
            quality_config["num_ctx"] = min(quality_config["num_ctx"] * 2, 8192)
            
        return quality_config

    def create_custom_llm(self, **kwargs) -> OllamaLLM:
        """Create LLM with custom parameters, falling back to optimized defaults."""
        
        # Start with optimized configuration
        config = self.get_optimized_config()
        
        # Override with custom parameters
        config.update(kwargs)
        
        # Validate and create
        validated_config = self._validate_parameters(config)
        return OllamaLLM(**validated_config)
