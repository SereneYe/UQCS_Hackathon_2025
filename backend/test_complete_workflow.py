#!/usr/bin/env python3
"""
完整工作流程测试脚本
测试 OpenAI + VEO3 集成的完整内容生成流程
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_veo3_service():
    """测试VEO3服务"""
    print("🎬 测试VEO3视频生成服务")
    print("=" * 50)
    
    # Check API key
    veo3_key = os.getenv("VEO3_API_KEY")
    if not veo3_key:
        print("❌ 请在.env文件中设置VEO3_API_KEY")
        print("   示例: VEO3_API_KEY=your-veo3-key-here")
        return False
    
    print(f"✅ VEO3 API密钥已配置 (长度: {len(veo3_key)})")
    
    try:
        from app.services.veo3_service import veo3_service
        print("✅ VEO3服务导入成功")
        
        # Test video generation with a simple prompt
        print("\n🎥 测试视频生成...")
        test_prompt = "A beautiful sunset over the ocean with gentle waves"
        output_video_id = 12345  # Test ID
        
        result = await veo3_service.generate_video_complete(
            prompt=test_prompt,
            output_video_id=output_video_id,
            model="veo3-fast",
            enhance_prompt=True
        )
        
        if result["success"]:
            print("✅ 视频生成成功!")
            print(f"  任务ID: {result.get('task_id', 'N/A')}")
            print(f"  输出路径: {result.get('output_path', 'N/A')}")
            print(f"  文件大小: {result.get('file_size', 0)} bytes")
            print(f"  耗时: {result.get('elapsed_seconds', 0):.1f} 秒")
            return True
        else:
            print(f"❌ 视频生成失败: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

async def test_complete_workflow():
    """测试完整工作流程"""
    print("\n🔄 测试完整工作流程 (OpenAI + VEO3)")
    print("=" * 50)
    
    # Check both API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    veo3_key = os.getenv("VEO3_API_KEY")
    
    if not openai_key:
        print("❌ 缺少OPENAI_API_KEY")
        return False
    
    if not veo3_key:
        print("❌ 缺少VEO3_API_KEY")
        return False
    
    print("✅ 所有API密钥已配置")
    
    try:
        from app.services.openai_service import openai_service
        from app.services.veo3_service import veo3_service
        
        print("✅ 所有服务导入成功")
        
        # Step 1: Generate prompts with OpenAI
        print("\n📝 步骤1: OpenAI分析和prompt生成...")
        user_input = "制作一个科技感的产品展示视频，展现AI助手的强大功能"
        
        analysis_result = await openai_service.analyze_and_generate_prompts(
            user_input=user_input,
            user_context="科技产品宣传视频"
        )
        
        if not analysis_result["success"]:
            print(f"❌ OpenAI分析失败: {analysis_result.get('error', 'Unknown error')}")
            return False
        
        data = analysis_result["data"]
        video_prompt = data.get("video_prompt")
        audio_prompt = data.get("audio_prompt")
        
        print("✅ OpenAI分析成功!")
        print(f"🎬 视频prompt: {video_prompt[:100]}...")
        print(f"🎵 音频prompt: {audio_prompt[:100]}...")
        
        # Step 2: Generate video with VEO3
        print("\n🎥 步骤2: VEO3视频生成...")
        output_video_id = 67890  # Test ID
        
        video_result = await veo3_service.generate_video_complete(
            prompt=video_prompt,
            output_video_id=output_video_id,
            model="veo3-fast",
            enhance_prompt=True
        )
        
        if video_result["success"]:
            print("✅ 完整工作流程成功!")
            print(f"  视频路径: {video_result.get('output_path', 'N/A')}")
            print(f"  文件大小: {video_result.get('file_size', 0)} bytes")
            print(f"  总耗时: {video_result.get('elapsed_seconds', 0):.1f} 秒")
            return True
        else:
            print(f"❌ VEO3视频生成失败: {video_result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ 工作流程异常: {str(e)}")
        return False

async def test_api_endpoints():
    """测试API端点（需要服务运行）"""
    print("\n📡 测试API端点")
    print("=" * 50)
    
    try:
        import requests
        base_url = "http://localhost:8000"
        
        # Test health check
        print("🏥 测试健康检查...")
        health_response = requests.get(f"{base_url}/content-generation/health", timeout=5)
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ 健康检查通过: {health_data.get('status', 'unknown')}")
            
            # Test complete workflow endpoint if both services are healthy
            if health_data.get("status") == "healthy":
                print("\n🔄 测试完整工作流程API...")
                
                payload = {
                    "user_input": "制作一个关于春天花开的唯美视频",
                    "user_context": "艺术欣赏",
                    "output_video_id": 99999,
                    "veo3_model": "veo3-fast",
                    "enhance_prompt": True
                }
                
                workflow_response = requests.post(
                    f"{base_url}/content-generation/complete-workflow",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=300  # 5 minutes for video generation
                )
                
                if workflow_response.status_code == 200:
                    workflow_data = workflow_response.json()
                    if workflow_data.get("success"):
                        print("✅ 完整工作流程API测试成功!")
                        video_gen = workflow_data.get("video_generation", {})
                        print(f"  视频ID: {video_gen.get('video_id', 'N/A')}")
                        print(f"  任务ID: {video_gen.get('task_id', 'N/A')}")
                        return True
                    else:
                        print(f"❌ 工作流程失败: {workflow_data.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ API调用失败: {workflow_response.status_code}")
                    return False
            else:
                print("⚠️  服务状态不完整，跳过工作流程测试")
                return True
        else:
            print(f"❌ 健康检查失败: {health_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  API服务未运行，跳过API测试")
        print("提示: 启动服务 - uvicorn app.main:app --reload")
        return True
    except Exception as e:
        print(f"❌ API测试异常: {str(e)}")
        return False

async def main():
    """主测试函数"""
    print("🚀 VEO3 + OpenAI 完整工作流程测试")
    print("=" * 80)
    
    success_count = 0
    total_tests = 3
    
    # 运行所有测试
    tests = [
        ("VEO3服务测试", test_veo3_service),
        ("完整工作流程测试", test_complete_workflow), 
        ("API端点测试", test_api_endpoints)
    ]
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        try:
            if await test_func():
                success_count += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {str(e)}")
    
    # 总结
    print("\n" + "=" * 80)
    print(f"📊 测试总结: {success_count}/{total_tests} 通过")
    
    if success_count == total_tests:
        print("🎉 所有测试通过! 完整工作流程正常运行")
        print("\n🚀 你现在可以:")
        print("1. 使用 /content-generation/analyze 接口生成双prompt")
        print("2. 使用 /content-generation/generate-video 接口生成视频")
        print("3. 使用 /content-generation/complete-workflow 接口运行完整流程")
        print("4. 集成到前端应用中")
    else:
        print("⚠️  部分测试失败")
        print("\n🔧 检查清单:")
        print("1. 确保已设置OPENAI_API_KEY和VEO3_API_KEY")
        print("2. 确保网络连接正常")
        print("3. 确保API密钥有效且有余额")

if __name__ == "__main__":
    asyncio.run(main())
