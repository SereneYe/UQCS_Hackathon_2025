#!/usr/bin/env python3
"""
简化的OpenAI服务测试脚本
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_openai_simple():
    """简单测试OpenAI服务"""
    
    print("🧪 简化OpenAI测试")
    print("=" * 50)
    
    # Check API key first
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 请在.env文件中设置OPENAI_API_KEY")
        print("   示例: OPENAI_API_KEY=sk-your-key-here")
        return False
    
    print(f"✅ API密钥已配置 (长度: {len(api_key)})")
    
    try:
        # Import the service
        from app.services.openai_service import OpenAIService
        print("✅ OpenAI服务导入成功")
        
        # Test the service with proper resource management
        print("\n📝 测试内容分析...")
        user_input = "制作一个关于猫咪玩耍的可爱视频"
        
        # Use the service as a context manager for proper cleanup
        async with OpenAIService() as service:
            result = await service.analyze_and_generate_prompts(
                user_input=user_input,
                user_context="用于宠物店宣传"
            )
            
            if result['success']:
                print("✅ 分析成功!")
                data = result['data']
                
                print(f"\n🎬 视频提示词:")
                print(f"   {data.get('video_prompt', 'N/A')[:100]}...")
                
                print(f"\n🎵 音频提示词:")
                print(f"   {data.get('audio_prompt', 'N/A')[:100]}...")
                
                if 'usage' in result:
                    usage = result['usage']
                    print(f"\n📊 API使用: {usage.get('total_tokens', 0)} tokens")
                
                return True
            else:
                print(f"❌ 分析失败: {result.get('error', 'Unknown error')}")
                return False
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        if "module" in str(e).lower():
            print("提示: 可能需要先安装依赖: pip install openai")
        return False

async def main():
    """主函数"""
    print("🚀 开始简化测试\n")
    
    success = await test_openai_simple()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ 测试通过! OpenAI服务工作正常")
        print("\n🚀 你现在可以:")
        print("1. 启动API服务: uvicorn app.main:app --reload")
        print("2. 测试API接口")
    else:
        print("❌ 测试失败")
        print("\n🔧 检查清单:")
        print("1. 确保已设置OPENAI_API_KEY环境变量")
        print("2. 确保网络连接正常")
        print("3. 确保API密钥有效且有余额")

if __name__ == "__main__":
    asyncio.run(main())
