# Enhanced JARVIS Voice Assistant with Wake Word Interruption
# Fixed version with all improvements from conversation history

from langchain_ollama import OllamaLLM  # Updated import
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferWindowMemory
import speech_recognition as sr
import win32com.client
import time
import threading
import queue
import os
import pvporcupine
import pyaudio
import struct
import re


class Jarvis:
    def __init__(self, wake_word="jarvis", speech_rate=4):
        print("🚀 Initializing Enhanced JARVIS...")
        
        # Initialize speech components FIRST to prevent AttributeError
        self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
        self.speaker.Rate = speech_rate
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 350
        self.recognizer.dynamic_energy_threshold = True
        
        # Audio initialization
        self.pa = pyaudio.PyAudio()
        self.setup_wake_word_detector(wake_word)
        
        # Enhanced response control flags
        self.currently_speaking = False
        self.interrupt_flag = threading.Event()
        self.processing_response = False  # Added missing attribute
        self.response_lock = threading.Lock()  # Added missing attribute
        
        # Create optimized LLM with error handling
        try:
            self.llm = OllamaLLM(
                model="deepseek-r1",
                temperature=0.5,      # Optimized for speed
                num_ctx=2048,         # Context window
                # Removed deprecated parameters: num_thread, num_predict, top_p
            )
            print("✅ LLM initialized successfully")
        except Exception as e:
            print(f"❌ LLM initialization failed: {e}")
            # Fallback to basic configuration
            self.llm = OllamaLLM(model="deepseek-r1")
        
        # Memory system
        self.memory = ConversationBufferWindowMemory(
            k=2,
            return_messages=True,
            memory_key="history"
        )
        
        self.chain = self.create_chain()
        
        # Threading setup
        self.speech_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.speech_thread = threading.Thread(target=self.speech_handler, daemon=True)
        self.wake_thread = threading.Thread(target=self.wake_word_listener, daemon=True)
        self.speech_thread.start()
        self.wake_thread.start()
        
        print("✅ Enhanced JARVIS initialized successfully!")
    
    def setup_wake_word_detector(self, wake_word):
        """Initialize wake word detection with error handling"""
        try:
            self.porcupine = pvporcupine.create(
                access_key="Enter your Key",
                keyword_paths=[r"C:\Users\Devesh\Desktop\genai\Jarvis_en_windows_v3_0_0.ppn"],
                model_path=r"C:\Users\Devesh\Desktop\genai\porcupine_params.pv"
            )
            self.audio_stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length,
                stream_callback=self.wake_word_callback
            )
            print("✅ Wake word detector initialized")
        except Exception as e:
            print(f"❌ Wake word init error: {e}")
            raise
    
    def wake_word_callback(self, in_data, frame_count, time_info, status):
        """Async wake word detection with proper threading"""
        try:
            pcm = struct.unpack_from("h" * self.porcupine.frame_length, in_data)
            if self.porcupine.process(pcm) >= 0:
                # Use separate thread to avoid blocking audio callback
                threading.Thread(target=self.on_wake_word_detected, daemon=True).start()
        except Exception as e:
            print(f"❌ Wake word callback error: {e}")
        return (None, pyaudio.paContinue)
    
    def on_wake_word_detected(self):
        """Enhanced wake word handler with proper interruption"""
        print("\n🟢 Wake word detected!")
        
        # CRITICAL: Immediately stop all ongoing operations
        self.interrupt_flag.set()
        
        # Stop current speech aggressively
        if self.currently_speaking:
            print("🛑 Interrupting speech...")
            try:
                self.speaker.Speak("")  # Empty string stops current speech
                # Additional interruption method for Windows SAPI
                self.speaker.Skip("Sentence")
            except:
                pass
            time.sleep(0.1)  # Brief pause for coordination
        
        # Clear all queues and reset flags
        self.clear_all_queues()
        self.currently_speaking = False
        self.processing_response = False
        
        # Wait for everything to stop
        time.sleep(0.3)
        
        # Now respond to wake word
        self.interrupt_flag.clear()
        self.speak_immediately("Yes sir?")
        
        # Listen for command
        command = self.listen(timeout=6)
        if command:
            self.process_command(command)
    
    def clear_all_queues(self):
        """Clear all pending speech - ADDED MISSING METHOD"""
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except queue.Empty:
                break
    
    def speak_immediately(self, text):
        """Speak text immediately without queuing - ADDED MISSING METHOD"""
        if not text:
            return
        
        # Stop any current speech first
        if self.currently_speaking:
            try:
                self.speaker.Speak("")  # Stop current speech
            except:
                pass
        
        # Speak immediately
        self.currently_speaking = True
        try:
            self.speaker.Speak(text)
        except Exception as e:
            print(f"❌ Speech error: {e}")
        finally:
            self.currently_speaking = False
    
    def get_system_prompt(self):
        """Optimized system prompt for better performance"""
        return """You are JARVIS, an AI assistant. Guidelines:
        1. Be concise and direct (1-2 sentences preferred)
        2. Respond naturally and conversationally
        3. If interrupted, stop immediately and wait for new commands
        4. Focus on the core information requested"""
    
    def create_chain(self):
        """Create the LLM processing chain"""
        try:
            return ChatPromptTemplate.from_messages([
                ("system", self.get_system_prompt()),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}")
            ]) | self.llm | StrOutputParser()
        except Exception as e:
            print(f"❌ Chain creation error: {e}")
            raise
    
    def listen(self, timeout=5):
        """Listen for voice input with error handling"""
        if not hasattr(self, 'recognizer'):
            print("❌ Recognizer not initialized")
            return ""
            
        with sr.Microphone() as source:
            try:
                print("🎤 Listening...", end='', flush=True)
                # Quick ambient noise adjustment
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=6)
                text = self.recognizer.recognize_google(audio).lower()
                print(f"\r👤 You: {text}")
                return text
            except sr.WaitTimeoutError:
                print("\r⏱️  No input detected")
                return ""
            except Exception as e:
                print(f"\r❌ Listen error: {e}")
                return ""
    
    def process_command(self, command):
        """Process voice command with enhanced response handling"""
        if not command.strip():
            return
        
        # Handle exit commands
        if any(word in command for word in ["exit", "stop", "quit", "shutdown"]):
            self.speak_immediately("Shutting down systems")
            self.stop_event.set()
            return
        
        # Set processing state
        with self.response_lock:
            self.processing_response = True
            self.interrupt_flag.clear()
            self.clear_all_queues()
        
        # Process in separate thread to avoid blocking
        threading.Thread(
            target=self.generate_buffered_response,
            args=(command,),
            daemon=True
        ).start()
    
    def generate_buffered_response(self, command):
        """Generate response with sentence buffering - ENHANCED VERSION"""
        try:
            sentence_buffer = ""
            full_response = ""
            
            print(f"\n🤖 JARVIS: ", end='', flush=True)
            
            # Stream response from LLM
            for chunk in self.chain.stream({
                "input": command,
                "history": self.memory.load_memory_variables({})["history"]
            }):
                if self.interrupt_flag.is_set():
                    print("\n🛑 Response generation interrupted!")
                    return
                
                sentence_buffer += chunk
                full_response += chunk
                print(chunk, end='', flush=True)
                
                # Check for complete sentences
                if self.is_sentence_complete(sentence_buffer):
                    self.speak_sentence(sentence_buffer.strip())
                    sentence_buffer = ""
            
            # Handle any remaining text
            if sentence_buffer.strip():
                self.speak_sentence(sentence_buffer.strip())
            
            print()  # New line after response
            
            # Save to memory
            self.memory.save_context({"input": command}, {"output": full_response})
            
        except Exception as e:
            print(f"\n❌ Response generation error: {e}")
            self.speak_immediately("I'm having trouble processing that request.")
        finally:
            self.processing_response = False
    
    def is_sentence_complete(self, text):
        """Check if text contains a complete sentence"""
        return bool(re.search(r'[.!?]+\s*', text) and len(text.strip()) > 10)
    
    def speak_sentence(self, sentence):
        """Speak a complete sentence with interrupt checking"""
        if not sentence or self.interrupt_flag.is_set():
            return
        
        # Clean the sentence
        cleaned = self.clean_sentence(sentence)
        if not cleaned:
            return
        
        # Add to speech queue
        self.speech_queue.put(cleaned)
    
    def clean_sentence(self, sentence):
        """Clean sentence for speech synthesis"""
        # Remove markdown formatting
        sentence = re.sub(r'\*\*([^*]+)\*\*', r'\1', sentence)  # Bold
        sentence = re.sub(r'\*([^*]+)\*', r'\1', sentence)      # Italic
        sentence = re.sub(r'`([^`]+)`', r'\1', sentence)        # Code
        sentence = re.sub(r'#{1,6}\s+', '', sentence)          # Headers
        
        # Clean whitespace
        sentence = ' '.join(sentence.split())
        sentence = sentence.replace('\n', ' ')
        
        return sentence.strip()
    
    def speak_interruptible(self, text):
        """Speech that can be interrupted"""
        if not text or self.interrupt_flag.is_set():
            return
            
        self.currently_speaking = True
        try:
            self.speaker.Speak(text)
        except Exception as e:
            print(f"❌ Speech error: {e}")
        finally:
            self.currently_speaking = False
    
    def speak(self, text):
        """Queue speech output"""
        if text:
            self.speech_queue.put(text)
    
    def speech_handler(self):
        """Enhanced speech handler with interrupt checking"""
        while not self.stop_event.is_set():
            try:
                # Get speech from queue with timeout
                text = self.speech_queue.get(timeout=0.1)
                
                # Check for interruption before speaking
                if not self.interrupt_flag.is_set():
                    self.speak_interruptible(text)
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Speech handler error: {e}")
    
    def wake_word_listener(self):
        """Wake word detection thread"""
        try:
            self.audio_stream.start_stream()
            print("🔴 Wake word detection active (say 'jarvis' to activate)")
            
            while not self.stop_event.is_set():
                time.sleep(0.1)
                
        except Exception as e:
            print(f"❌ Wake word listener error: {e}")
        finally:
            if hasattr(self, 'audio_stream'):
                self.audio_stream.stop_stream()
    
    def run(self):
        """Main execution loop with enhanced error handling"""
        self.speak("Enhanced systems ready. Say jarvis to begin.")
        
        try:
            while not self.stop_event.is_set():
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt received")
            self.stop_event.set()
        except Exception as e:
            print(f"❌ Runtime error: {e}")
            self.stop_event.set()
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up resources...")
        
        # Stop all threads
        self.stop_event.set()
        
        # Close audio streams
        try:
            if hasattr(self, 'audio_stream'):
                self.audio_stream.close()
            if hasattr(self, 'pa'):
                self.pa.terminate()
            if hasattr(self, 'porcupine'):
                self.porcupine.delete()
        except Exception as e:
            print(f"❌ Cleanup error: {e}")
        
        print("✅ Cleanup complete!")


if __name__ == "__main__":
    print("🚀 Starting Enhanced JARVIS Voice Assistant...")
    print("💡 Features:")
    print("   ✅ Wake word interruption")
    print("   ✅ Sentence-level speech synthesis")
    print("   ✅ Enhanced error handling")
    print("   ✅ Updated LangChain integration")
    print()
    
    try:
        assistant = Jarvis(wake_word="jarvis", speech_rate=4)
        assistant.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        import traceback
        traceback.print_exc()