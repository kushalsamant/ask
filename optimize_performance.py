#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Optimization Script for ASK Research Tool
Heavy optimization and performance tuning
"""

import os
import sys
import time
import json
import psutil
import gc
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import subprocess

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('optimization_results.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Performance optimization for ASK research tool"""
    
    def __init__(self):
        self.optimization_results = {}
        self.start_time = time.time()
        self.baseline_metrics = {}
        self.optimized_metrics = {}
        
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            import psutil
            
            # CPU information
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory information
            memory = psutil.virtual_memory()
            
            # Disk information
            disk = psutil.disk_usage('/')
            
            # Network information
            network = psutil.net_io_counters()
            
            system_info = {
                'cpu': {
                    'count': cpu_count,
                    'frequency_mhz': cpu_freq.current if cpu_freq else None,
                    'usage_percent': cpu_percent
                },
                'memory': {
                    'total_gb': memory.total / (1024**3),
                    'available_gb': memory.available / (1024**3),
                    'used_percent': memory.percent
                },
                'disk': {
                    'total_gb': disk.total / (1024**3),
                    'free_gb': disk.free / (1024**3),
                    'used_percent': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv
                }
            }
            
            return system_info
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}
    
    def measure_baseline_performance(self) -> Dict[str, Any]:
        """Measure baseline performance metrics"""
        logger.info("📊 Measuring Baseline Performance...")
        
        baseline = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self.get_system_info(),
            'import_times': {},
            'memory_usage': {},
            'disk_usage': {}
        }
        
        # Measure import times
        modules_to_test = [
            'main',
            'research_orchestrator',
            'image_generation_system',
            'smart_image_generator',
            'api_client'
        ]
        
        for module in modules_to_test:
            try:
                start_time = time.time()
                __import__(module)
                import_time = time.time() - start_time
                baseline['import_times'][module] = import_time
                logger.info(f"  {module}: {import_time:.3f}s")
            except ImportError as e:
                logger.warning(f"  {module}: Import failed - {e}")
                baseline['import_times'][module] = None
        
        # Measure memory usage
        process = psutil.Process()
        baseline['memory_usage']['current_mb'] = process.memory_info().rss / (1024 * 1024)
        
        # Measure disk usage
        baseline['disk_usage']['current_mb'] = sum(
            os.path.getsize(os.path.join(root, file))
            for root, dirs, files in os.walk('.')
            for file in files
        ) / (1024 * 1024)
        
        self.baseline_metrics = baseline
        return baseline
    
    def optimize_imports(self) -> Dict[str, Any]:
        """Optimize module imports"""
        logger.info("⚡ Optimizing Module Imports...")
        
        optimization_results = {
            'lazy_imports': {},
            'import_optimization': {},
            'recommendations': []
        }
        
        # Check for lazy imports
        modules_with_lazy_imports = [
            'torch',
            'diffusers',
            'transformers',
            'accelerate'
        ]
        
        for module in modules_with_lazy_imports:
            try:
                start_time = time.time()
                __import__(module)
                import_time = time.time() - start_time
                
                if import_time > 2.0:  # If import takes more than 2 seconds
                    optimization_results['lazy_imports'][module] = {
                        'import_time': import_time,
                        'recommendation': 'Use lazy imports'
                    }
                    optimization_results['recommendations'].append(
                        f"Consider lazy import for {module} (takes {import_time:.2f}s)"
                    )
                    
            except ImportError:
                optimization_results['lazy_imports'][module] = {
                    'import_time': None,
                    'recommendation': 'Module not available'
                }
        
        # Check for unused imports
        optimization_results['recommendations'].append(
            "Run 'python -m flake8' to check for unused imports"
        )
        
        self.optimization_results['imports'] = optimization_results
        return optimization_results
    
    def optimize_memory_usage(self) -> Dict[str, Any]:
        """Optimize memory usage"""
        logger.info("🧠 Optimizing Memory Usage...")
        
        optimization_results = {
            'current_memory_mb': 0,
            'memory_optimizations': [],
            'recommendations': []
        }
        
        # Get current memory usage
        process = psutil.Process()
        current_memory = process.memory_info().rss / (1024 * 1024)
        optimization_results['current_memory_mb'] = current_memory
        
        # Memory optimization recommendations
        if current_memory > 500:  # If using more than 500MB
            optimization_results['memory_optimizations'].append({
                'issue': 'High memory usage',
                'current': f"{current_memory:.1f}MB",
                'recommendation': 'Consider garbage collection and memory cleanup'
            })
            optimization_results['recommendations'].append(
                "Enable garbage collection after heavy operations"
            )
        
        # Check for memory leaks
        optimization_results['recommendations'].append(
            "Monitor memory usage during long-running operations"
        )
        
        # GPU memory optimization
        try:
            import torch
            if torch.cuda.is_available():
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                optimization_results['memory_optimizations'].append({
                    'issue': 'GPU memory available',
                    'current': f"{gpu_memory:.1f}GB",
                    'recommendation': 'Use GPU memory efficiently'
                })
                optimization_results['recommendations'].append(
                    "Enable attention slicing and VAE slicing for GPU memory optimization"
                )
        except ImportError:
            pass
        
        self.optimization_results['memory'] = optimization_results
        return optimization_results
    
    def optimize_disk_usage(self) -> Dict[str, Any]:
        """Optimize disk usage"""
        logger.info("💾 Optimizing Disk Usage...")
        
        optimization_results = {
            'current_disk_mb': 0,
            'disk_optimizations': [],
            'recommendations': []
        }
        
        # Calculate current disk usage
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk('.'):
            # Skip git and cache directories
            if '.git' in root or '__pycache__' in root or '.cache' in root:
                continue
                
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    file_count += 1
                except (OSError, FileNotFoundError):
                    continue
        
        optimization_results['current_disk_mb'] = total_size / (1024 * 1024)
        
        # Check for large files
        large_files = []
        for root, dirs, files in os.walk('.'):
            if '.git' in root or '__pycache__' in root:
                continue
                
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    if file_size > 10 * 1024 * 1024:  # Files larger than 10MB
                        large_files.append({
                            'file': file_path,
                            'size_mb': file_size / (1024 * 1024)
                        })
                except (OSError, FileNotFoundError):
                    continue
        
        if large_files:
            optimization_results['disk_optimizations'].append({
                'issue': 'Large files detected',
                'files': large_files,
                'recommendation': 'Consider compression or cleanup'
            })
            optimization_results['recommendations'].append(
                "Large files detected - consider adding to .gitignore"
            )
        
        # Check for temporary files
        temp_files = []
        for root, dirs, files in os.walk('.'):
            if '.git' in root:
                continue
                
            for file in files:
                if file.endswith(('.tmp', '.temp', '.log', '.cache')):
                    temp_files.append(os.path.join(root, file))
        
        if temp_files:
            optimization_results['disk_optimizations'].append({
                'issue': 'Temporary files found',
                'count': len(temp_files),
                'recommendation': 'Clean up temporary files'
            })
            optimization_results['recommendations'].append(
                f"Found {len(temp_files)} temporary files - consider cleanup"
            )
        
        self.optimization_results['disk'] = optimization_results
        return optimization_results
    
    def optimize_network_usage(self) -> Dict[str, Any]:
        """Optimize network usage"""
        logger.info("🌐 Optimizing Network Usage...")
        
        optimization_results = {
            'api_optimizations': [],
            'recommendations': []
        }
        
        # Check API configuration
        try:
            from dotenv import load_dotenv
            load_dotenv('ask.env')
            
            api_base = os.getenv('TOGETHER_API_BASE')
            rate_limit_delay = float(os.getenv('RATE_LIMIT_DELAY', '10.0'))
            
            if rate_limit_delay > 5.0:
                optimization_results['api_optimizations'].append({
                    'issue': 'High rate limit delay',
                    'current': f"{rate_limit_delay}s",
                    'recommendation': 'Consider reducing rate limit delay'
                })
                optimization_results['recommendations'].append(
                    "Reduce RATE_LIMIT_DELAY for faster API calls"
                )
            
            # Check for API timeout settings
            api_timeout = int(os.getenv('API_TIMEOUT', '60'))
            if api_timeout > 30:
                optimization_results['api_optimizations'].append({
                    'issue': 'High API timeout',
                    'current': f"{api_timeout}s",
                    'recommendation': 'Consider reducing timeout for faster failure detection'
                })
                optimization_results['recommendations'].append(
                    "Reduce API_TIMEOUT for faster error detection"
                )
                
        except Exception as e:
            logger.warning(f"Could not check API configuration: {e}")
        
        # Network optimization recommendations
        optimization_results['recommendations'].extend([
            "Use connection pooling for API requests",
            "Implement request caching for repeated calls",
            "Consider batch processing for multiple requests"
        ])
        
        self.optimization_results['network'] = optimization_results
        return optimization_results
    
    def optimize_image_generation(self) -> Dict[str, Any]:
        """Optimize image generation performance"""
        logger.info("🎨 Optimizing Image Generation...")
        
        optimization_results = {
            'gpu_optimizations': [],
            'cpu_optimizations': [],
            'recommendations': []
        }
        
        # Check GPU availability and optimization
        try:
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                
                optimization_results['gpu_optimizations'].append({
                    'device': gpu_name,
                    'memory_gb': gpu_memory,
                    'status': 'Available'
                })
                
                # GPU-specific optimizations
                if gpu_memory < 6:  # Less than 6GB
                    optimization_results['recommendations'].extend([
                        "Enable attention slicing for memory optimization",
                        "Use VAE slicing for large images",
                        "Consider using CPU offload for large models"
                    ])
                else:
                    optimization_results['recommendations'].extend([
                        "Use higher resolution images",
                        "Increase batch size for faster processing",
                        "Use more inference steps for better quality"
                    ])
            else:
                optimization_results['gpu_optimizations'].append({
                    'status': 'Not available',
                    'recommendation': 'Use CPU optimization'
                })
                
        except ImportError:
            optimization_results['gpu_optimizations'].append({
                'status': 'PyTorch not available',
                'recommendation': 'Install PyTorch for GPU support'
            })
        
        # CPU optimizations
        optimization_results['cpu_optimizations'].extend([
            {
                'optimization': 'Use LCM models for faster generation',
                'recommendation': 'Set CPU_MODEL_ID to LCM-SD15'
            },
            {
                'optimization': 'Reduce inference steps',
                'recommendation': 'Use 4-8 steps for faster generation'
            },
            {
                'optimization': 'Use smaller image sizes',
                'recommendation': 'Use 512x512 for faster generation'
            }
        ])
        
        self.optimization_results['image_generation'] = optimization_results
        return optimization_results
    
    def generate_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        logger.info("📋 Generating Optimization Report...")
        
        # Run all optimizations
        baseline = self.measure_baseline_performance()
        import_opt = self.optimize_imports()
        memory_opt = self.optimize_memory_usage()
        disk_opt = self.optimize_disk_usage()
        network_opt = self.optimize_network_usage()
        image_opt = self.optimize_image_generation()
        
        # Compile recommendations
        all_recommendations = []
        all_recommendations.extend(import_opt.get('recommendations', []))
        all_recommendations.extend(memory_opt.get('recommendations', []))
        all_recommendations.extend(disk_opt.get('recommendations', []))
        all_recommendations.extend(network_opt.get('recommendations', []))
        all_recommendations.extend(image_opt.get('recommendations', []))
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'baseline_performance': baseline,
            'optimizations': {
                'imports': import_opt,
                'memory': memory_opt,
                'disk': disk_opt,
                'network': network_opt,
                'image_generation': image_opt
            },
            'summary': {
                'total_recommendations': len(all_recommendations),
                'priority_recommendations': [
                    rec for rec in all_recommendations 
                    if any(keyword in rec.lower() for keyword in ['high', 'critical', 'important'])
                ],
                'system_info': baseline.get('system_info', {})
            },
            'all_recommendations': all_recommendations
        }
        
        # Save report
        with open('optimization_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Log summary
        logger.info("=" * 80)
        logger.info("📊 OPTIMIZATION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Recommendations: {len(all_recommendations)}")
        logger.info(f"Priority Recommendations: {len(report['summary']['priority_recommendations'])}")
        logger.info(f"System Memory: {baseline.get('system_info', {}).get('memory', {}).get('total_gb', 0):.1f}GB")
        logger.info(f"Current Memory Usage: {memory_opt.get('current_memory_mb', 0):.1f}MB")
        logger.info(f"Current Disk Usage: {disk_opt.get('current_disk_mb', 0):.1f}MB")
        
        logger.info("\n🔧 TOP RECOMMENDATIONS:")
        for i, rec in enumerate(all_recommendations[:5], 1):
            logger.info(f"  {i}. {rec}")
        
        logger.info("\n📄 Full report saved to optimization_report.json")
        
        return report
    
    def apply_optimizations(self) -> Dict[str, Any]:
        """Apply recommended optimizations"""
        logger.info("🔧 Applying Optimizations...")
        
        applied_optimizations = {
            'applied': [],
            'failed': [],
            'manual_required': []
        }
        
        # Apply automatic optimizations
        try:
            # Clean up temporary files
            temp_files_cleaned = 0
            for root, dirs, files in os.walk('.'):
                if '.git' in root:
                    continue
                    
                for file in files:
                    if file.endswith(('.tmp', '.temp', '.cache')):
                        try:
                            os.remove(os.path.join(root, file))
                            temp_files_cleaned += 1
                        except (OSError, FileNotFoundError):
                            continue
            
            if temp_files_cleaned > 0:
                applied_optimizations['applied'].append({
                    'optimization': 'Clean temporary files',
                    'result': f"Cleaned {temp_files_cleaned} files"
                })
            
            # Force garbage collection
            gc.collect()
            applied_optimizations['applied'].append({
                'optimization': 'Garbage collection',
                'result': 'Memory cleaned'
            })
            
        except Exception as e:
            applied_optimizations['failed'].append({
                'optimization': 'Automatic cleanup',
                'error': str(e)
            })
        
        # Manual optimizations required
        applied_optimizations['manual_required'].extend([
            "Update .gitignore for better file management",
            "Configure environment variables for optimal performance",
            "Review and optimize API settings",
            "Consider hardware upgrades if needed"
        ])
        
        logger.info(f"✅ Applied {len(applied_optimizations['applied'])} optimizations")
        logger.info(f"❌ Failed {len(applied_optimizations['failed'])} optimizations")
        logger.info(f"📝 Manual actions required: {len(applied_optimizations['manual_required'])}")
        
        return applied_optimizations

def main():
    """Main optimization function"""
    optimizer = PerformanceOptimizer()
    
    # Generate optimization report
    report = optimizer.generate_optimization_report()
    
    # Apply optimizations
    applied = optimizer.apply_optimizations()
    
    # Save final results
    final_results = {
        'report': report,
        'applied_optimizations': applied,
        'timestamp': datetime.now().isoformat()
    }
    
    with open('final_optimization_results.json', 'w') as f:
        json.dump(final_results, f, indent=2)
    
    logger.info("🎉 Optimization complete! Check final_optimization_results.json for details.")

if __name__ == "__main__":
    main()
