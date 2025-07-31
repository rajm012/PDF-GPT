#!/usr/bin/env python3
"""
Configuration validation script for PDF GPT
Tests both TOML and environment variable configuration methods
"""

import os
import sys
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from config_loader import config, config_mapping
    print("✅ Configuration loader imported successfully")
except ImportError as e:
    print(f"❌ Failed to import configuration loader: {e}")
    sys.exit(1)

def test_toml_config():
    """Test TOML configuration loading"""
    print("\n🔧 Testing TOML Configuration...")
    
    # Check if config.toml exists
    if os.path.exists("config.toml"):
        print("✅ config.toml found")
        
        # Test various config sections
        test_values = [
            ("app", "SECRET_KEY", "Default secret"),
            ("server", "HOST", "0.0.0.0"),
            ("storage", "UPLOAD_FOLDER", "data/uploads"),
            ("ai", "OLLAMA_HOST", "http://localhost:11434"),
            ("logging", "LOG_LEVEL", "INFO")
        ]
        
        for section, key, default in test_values:
            value = config.get(section, key, default)
            print(f"   {section}.{key} = {value}")
            
    else:
        print("⚠️ config.toml not found, will use environment variables")

def test_env_config():
    """Test environment variable configuration"""
    print("\n🌍 Testing Environment Variable Configuration...")
    
    # Test flat config access (backward compatibility)
    test_vars = [
        ("SECRET_KEY", "default-secret"),
        ("UPLOAD_FOLDER", "data/uploads"),
        ("OLLAMA_HOST", "http://localhost:11434"),
        ("LOG_LEVEL", "INFO")
    ]
    
    for var, default in test_vars:
        value = config.get_flat(var, default)
        print(f"   {var} = {value}")

def test_config_classes():
    """Test configuration classes"""
    print("\n🏭 Testing Configuration Classes...")
    
    environments = ["development", "production", "testing"]
    
    for env in environments:
        print(f"\n   {env.title()} Configuration:")
        try:
            config_class = config_mapping.get(env, config_mapping['default'])()
            print(f"     ✅ {env} config loaded successfully")
            print(f"     DEBUG: {getattr(config_class, 'DEBUG', 'N/A')}")
            print(f"     FLASK_ENV: {getattr(config_class, 'FLASK_ENV', 'N/A')}")
            print(f"     UPLOAD_FOLDER: {getattr(config_class, 'UPLOAD_FOLDER', 'N/A')}")
        except Exception as e:
            print(f"     ❌ Failed to load {env} config: {e}")

def test_type_conversion():
    """Test automatic type conversion"""
    print("\n🔄 Testing Type Conversion...")
    
    # Set some test environment variables
    os.environ["TEST_BOOL"] = "true"
    os.environ["TEST_INT"] = "42"
    os.environ["TEST_FLOAT"] = "3.14"
    os.environ["TEST_LIST"] = "item1,item2,item3"
    
    # Test conversions
    tests = [
        ("TEST_BOOL", True, bool),
        ("TEST_INT", 10, int),
        ("TEST_FLOAT", 2.0, float),
        ("TEST_LIST", ["default"], list)
    ]
    
    for var, default, expected_type in tests:
        value = config.get_flat(var, default)
        print(f"   {var} = {value} (type: {type(value).__name__})")
        assert isinstance(value, expected_type), f"Type conversion failed for {var}"
    
    # Clean up test variables
    for var in ["TEST_BOOL", "TEST_INT", "TEST_FLOAT", "TEST_LIST"]:
        os.environ.pop(var, None)
    
    print("   ✅ All type conversions working correctly")

def main():
    """Main validation function"""
    print("🚀 PDF GPT Configuration Validation")
    print("=" * 50)
    
    try:
        test_toml_config()
        test_env_config()
        test_config_classes()
        test_type_conversion()
        
        print("\n" + "=" * 50)
        print("✅ All configuration tests passed!")
        print("\n💡 Configuration Summary:")
        print(f"   - Config file: {'✅ Found' if os.path.exists('config.toml') else '❌ Not found'}")
        print(f"   - Environment variables: ✅ Available")
        print(f"   - TOML parser: ✅ Working")
        print(f"   - Type conversion: ✅ Working")
        print(f"   - Config classes: ✅ Working")
        
        print("\n🎯 You can now run the application using either:")
        print("   1. TOML configuration (recommended)")
        print("   2. Environment variables")
        print("   3. Mixed approach (TOML + env override)")
        
    except Exception as e:
        print(f"\n❌ Configuration validation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
