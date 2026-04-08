# 🚚 Delivery Route Optimization Environment

[![OpenEnv Compatible](https://img.shields.io/badge/OpenEnv-Compatible-blue)](https://github.com/meta-pytorch/OpenEnv)
[![Hugging Face Spaces](https://img.shields.io/badge/🤗%20Spaces-Delivery%20Route%20Env-yellow)](https://huggingface.co/spaces)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://www.docker.com/)

A production-ready, OpenEnv-compliant reinforcement learning environment for optimizing delivery routes with real-world constraints including time windows, vehicle capacity, traffic conditions, and priority-based deliveries.

<p align="center">
  <img src="https://via.placeholder.com/800x400/0066cc/ffffff?text=Delivery+Route+Optimization+Environment" alt="Delivery Route Environment" width="800"/>
</p>

## 🎯 Features

### ✅ Core Requirements Met
- **🌍 Real-World Task**: Simulates actual delivery operations with NYC-based locations
- **📊 3 Difficulty Levels**: Easy (5 stops), Medium (12 stops), Hard (20 stops)
- **🎁 Partial Reward Signals**: Granular rewards for time windows, priorities, and efficiency
- **🐳 Docker + HF Spaces**: Fully containerized with Hugging Face Spaces deployment
- **📝 Strict Logging**: JSON-structured logging with session tracking and performance metrics

### 🚀 Advanced Features
- **⏰ Time Window Constraints**: Deliveries must occur within specified time ranges
- **📦 Capacity Management**: Vehicle weight limits with real-time tracking
- **🚦 Dynamic Traffic**: Traffic conditions affect travel times and update in real-time
- **⭐ Priority System**: 5-tier priority system for urgent deliveries
- **🗺️ Geographic Realism**: Actual NYC coordinates with Haversine distance calculations
- **📈 Performance Metrics**: Comprehensive tracking of delivery success rates and efficiency

## 📦 Installation

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/delivery-route-env.git
cd delivery-route-env

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install OpenEnv CLI
pip install openenv
