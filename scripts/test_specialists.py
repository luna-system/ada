#!/usr/bin/env python3
"""
Test script to verify specialist plugin system.
Run from container or with proper Python path.
"""
import asyncio
import sys
import os

from brain.specialists import get_registry, list_specialists


async def main():
    print("=== Specialist Plugin System Test ===\n")
    
    # Get registry
    registry = get_registry()
    
    # List discovered specialists
    specialists = list_specialists()
    print(f"Discovered {len(specialists)} specialist(s):\n")
    
    for spec in specialists:
        cap = spec.capability
        print(f"  {cap.context_icon} {cap.name} v{cap.version}")
        print(f"     Description: {cap.description}")
        print(f"     Priority: {cap.context_priority.name} ({cap.context_priority.value})")
        print(f"     Tags: {', '.join(cap.tags)}")
        print(f"     Enabled: {cap.enabled}")
        print()
    
    # Test OCR specialist activation
    print("--- Testing OCR Specialist Activation ---")
    ocr_context = {
        'ocr_context': {
            'text': 'Hello World',
            'filename': 'test.png',
            'char_count': 11,
            'confidence': 95.5
        }
    }
    
    results = await registry.execute_for_context(ocr_context)
    print(f"Activated {len(results)} specialist(s) for OCR context")
    
    for result in results:
        print(f"\n  Specialist: {result.specialist_name}")
        print(f"  Success: {result.success}")
        if result.success:
            print(f"  Context preview: {result.context_text[:100]}...")
        else:
            print(f"  Error: {result.error}")
    
    # Test media specialist activation
    print("\n--- Testing Media Specialist Activation ---")
    media_context = {
        'media': {
            'status': 'playing',
            'track_name': 'Test Track',
            'artist_name': 'Test Artist'
        }
    }
    
    results = await registry.execute_for_context(media_context)
    print(f"Activated {len(results)} specialist(s) for media context")
    
    for result in results:
        print(f"\n  Specialist: {result.specialist_name}")
        print(f"  Success: {result.success}")
        if result.success:
            print(f"  Context preview: {result.context_text[:100]}...")
    
    print("\n=== Test Complete ===")


if __name__ == '__main__':
    asyncio.run(main())
