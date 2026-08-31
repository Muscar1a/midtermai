#!/usr/bin/env python3
"""
Rule-based distractor generation: mutate each correct answer to produce 3 plausible wrong variants.
No API calls. Mutations: term swaps, number changes, operator swaps.
Falls back to same-day topic-filtered cross-pollination if too few mutations apply.
"""

import json
import os
import re
import random
from collections import defaultdict

# ---------------------------------------------------------------------------
# Term swap rules: (regex_pattern, [wrong_replacements])
# Applied with re.IGNORECASE where the replacement is in the same case/style.
# ---------------------------------------------------------------------------
TERM_RULES = [
    # -----------------------------------------------------------------------
    # Latency metrics
    # -----------------------------------------------------------------------
    (r'\bTTFT\b', ['TBT', 'ITL', 'TPOT']),
    (r'\bTBT\b', ['TTFT', 'ITL', 'TPOT']),
    (r'\bITL\b', ['TTFT', 'TBT', 'TPOT']),
    (r'\bTPOT\b', ['TTFT', 'TBT', 'ITL']),

    # -----------------------------------------------------------------------
    # Formula variables
    # -----------------------------------------------------------------------
    (r'\bIn_Tokens\b', ['Out_Tokens', 'Total_Tokens']),
    (r'\bOut_Tokens\b', ['In_Tokens', 'Total_Tokens']),
    (r'\bP_in\b', ['P_out', 'P_avg']),
    (r'\bP_out\b', ['P_in', 'P_avg']),
    (r'\bGeneration_Time_Per_Token\b', ['Prefill_Time_Per_Token', 'Total_Time_Per_Token']),

    # Formula math operators (inside backtick formulas)
    (r'In_Tokens \* P_in \+ Out_Tokens \* P_out',
     ['In_Tokens + P_in * Out_Tokens + P_out',
      'In_Tokens * P_out + Out_Tokens * P_in',
      '(In_Tokens + Out_Tokens) * (P_in + P_out)']),
    (r'TTFT \+ \(Generation_Time_Per_Token \* Output_Tokens\)',
     ['TTFT * Generation_Time_Per_Token + Output_Tokens',
      'TTFT + Generation_Time_Per_Token / Output_Tokens',
      'TTFT - (Generation_Time_Per_Token * Output_Tokens)']),
    (r'\/ 1,000,000\b', ['/ 1,000', '* 1,000,000', '/ 1,000,000,000']),
    (r'\/ 1,000\b', ['/ 1,000,000', '* 1,000', '/ 100']),

    # -----------------------------------------------------------------------
    # Sampling strategies
    # -----------------------------------------------------------------------
    (r'\bGreedy Sampling\b', ['Top-k Sampling', 'Top-p Sampling', 'Random Sampling']),
    (r'\bGreedy Decoding\b', ['Top-p Sampling', 'Beam Search', 'Random Sampling']),
    (r'\bNucleus Sampling\b', ['Top-k Sampling', 'Greedy Sampling', 'Beam Search']),
    (r'\bTop-k Sampling\b', ['Top-p Sampling', 'Greedy Sampling', 'Beam Search']),
    (r'\bTop-p Sampling\b', ['Top-k Sampling', 'Greedy Sampling', 'Beam Search']),
    (r'\bBeam Search\b', ['Greedy Search', 'Top-p Sampling', 'Random Sampling']),
    (r'\bTop-k\b', ['Top-p', 'Greedy', 'Beam Search']),
    (r'\bTop-p\b', ['Top-k', 'Greedy', 'Beam Search']),
    (r'\bGreedy\b', ['Top-p', 'Top-k', 'Random']),

    # -----------------------------------------------------------------------
    # Architecture: attention, cache, layers
    # -----------------------------------------------------------------------
    (r'\bPrefill\b', ['Decoding', 'Tokenization', 'Embedding']),
    (r'\bDecoding\b', ['Prefill', 'Tokenization', 'Attention']),
    (r'\bKV Cache\b', ['Weight Cache', 'Activation Cache', 'Embedding Cache']),
    (r'\bPrompt Cache\b', ['KV Cache', 'Weight Cache', 'Activation Cache']),
    (r'\bMulti-Head Attention\b', ['Multi-Query Attention', 'Grouped-Query Attention', 'Cross-Attention']),
    (r'\bMQA\b', ['MHA', 'GQA', 'FlashAttention']),
    (r'\bGQA\b', ['MHA', 'MQA', 'FlashAttention']),
    (r'\bFlashAttention\b', ['PagedAttention', 'Multi-Head Attention', 'Sparse Attention']),
    (r'\bPagedAttention\b', ['FlashAttention', 'Chunked Prefill', 'Continuous Batching']),
    (r'\bContinuous Batching\b', ['Static Batching', 'Dynamic Batching', 'Micro-batching']),
    (r'\bSpeculative Decoding\b', ['Greedy Decoding', 'Beam Decoding', 'Parallel Decoding']),

    # -----------------------------------------------------------------------
    # Fine-tuning / alignment
    # -----------------------------------------------------------------------
    (r'\bRAG\b', ['LoRA', 'RLHF', 'SFT']),
    (r'\bLoRA\b', ['RAG', 'RLHF', 'QLoRA']),
    (r'\bQLoRA\b', ['LoRA', 'RLHF', 'RAG']),
    (r'\bRLHF\b', ['SFT', 'LoRA', 'DPO']),
    (r'\bSFT\b', ['RLHF', 'LoRA', 'DPO']),
    (r'\bDPO\b', ['SFT', 'RLHF', 'LoRA']),
    (r'\bPPO\b', ['DPO', 'RLHF', 'SFT']),

    # -----------------------------------------------------------------------
    # Tokenization — match full patterns first to avoid mixed-name mutations
    # -----------------------------------------------------------------------
    (r'Byte-Pair Encoding \(BPE\)', ['WordPiece', 'Unigram Language Model', 'SentencePiece']),
    (r'\bByte-Pair Encoding\b', ['WordPiece', 'Unigram Language Model', 'SentencePiece']),
    (r'\bBPE\b', ['WordPiece', 'Unigram', 'SentencePiece']),
    (r'\bWordPiece\b', ['BPE', 'Unigram', 'SentencePiece']),
    (r'\bUnigram Language Model\b', ['BPE', 'WordPiece', 'SentencePiece']),
    (r'\bSentencePiece\b', ['BPE', 'WordPiece', 'Unigram']),

    # -----------------------------------------------------------------------
    # Encoder/decoder architecture
    # -----------------------------------------------------------------------
    (r'\bencoder-only\b', ['decoder-only', 'encoder-decoder']),
    (r'\bdecoder-only\b', ['encoder-only', 'encoder-decoder']),
    (r'\bencoder-decoder\b', ['encoder-only', 'decoder-only']),
    (r'\bencoder\b', ['decoder', 'tokenizer']),
    (r'\bdecoder\b', ['encoder', 'tokenizer']),

    # -----------------------------------------------------------------------
    # Memory / hardware
    # -----------------------------------------------------------------------
    (r'\bVRAM\b', ['RAM', 'DRAM', 'NVMe SSD']),
    (r'\bGPU\b', ['CPU', 'TPU', 'FPGA']),
    (r'\bCPU\b', ['GPU', 'TPU', 'FPGA']),
    (r'\bNVIDIA\b', ['AMD', 'Intel', 'Google']),
    (r'\bH100\b', ['A100', 'V100', 'RTX 4090']),
    (r'\bA100\b', ['H100', 'V100', 'RTX 4090']),

    # -----------------------------------------------------------------------
    # Streaming / API / HTTP
    # -----------------------------------------------------------------------
    (r'\bstream=True\b', ['stream=False', 'async_mode=True', 'chunk=True']),
    (r'\bstream=False\b', ['stream=True', 'buffer=True', 'sync=True']),
    (r'\bServer-Sent Events \(SSE\)\b', ['WebSocket', 'Long Polling', 'gRPC Streaming']),
    (r'\bServer-Sent Events\b', ['WebSocket', 'Long Polling', 'gRPC Streaming']),
    (r'\bSSE\b', ['WebSocket', 'gRPC', 'HTTP/2 Push']),
    (r'\bWebSocket\b', ['SSE', 'Long Polling', 'HTTP/2 Push']),
    (r'\bExponential Backoff\b', ['Linear Backoff', 'Fixed Delay Retry', 'Fibonacci Backoff']),
    (r'\bJitter\b', ['Backoff', 'Timeout', 'Throttling']),
    (r'\bCircuit Breaker\b', ['Rate Limiter', 'Retry Policy', 'Bulkhead']),

    # -----------------------------------------------------------------------
    # Tool / framework names (confusion vocabulary)
    # -----------------------------------------------------------------------
    (r'\bPydantic\b', ['Marshmallow', 'dataclasses', 'attrs']),
    (r'\bLangGraph\b', ['AutoGen', 'CrewAI', 'Haystack']),
    (r'\bAutoGen\b', ['LangGraph', 'CrewAI', 'Haystack']),
    (r'\bCrewAI\b', ['LangGraph', 'AutoGen', 'Haystack']),
    (r'\bLangChain\b', ['LlamaIndex', 'Haystack', 'AutoGen']),
    (r'\bLlamaIndex\b', ['LangChain', 'Haystack', 'LangGraph']),
    (r'\bRAGAS\b', ['LangSmith', 'TruLens', 'PromptFlow']),
    (r'\bColang\b', ['YAML', 'Protobuf', 'ONNX']),
    (r'\bcreate_react_agent\b', ['create_openai_agent', 'create_tool_calling_agent', 'create_json_agent']),
    (r'\bJSON Schema\b', ['XML Schema', 'Protobuf Schema', 'Avro Schema']),
    (r'\bOpenLineage\b', ['DataHub', 'Marquez', 'Apache Atlas']),
    (r'\bMarquez\b', ['DataHub', 'Apache Atlas', 'Amundsen']),
    (r'\bFaiss\b', ['Weaviate', 'Pinecone', 'Qdrant']),
    (r'\bPinecone\b', ['Faiss', 'Weaviate', 'Qdrant']),
    (r'\bWeaviate\b', ['Faiss', 'Pinecone', 'Qdrant']),
    (r'\bChroma\b', ['Faiss', 'Pinecone', 'Weaviate']),
    (r'\bRedis\b', ['Memcached', 'DynamoDB', 'Cassandra']),
    (r'\bPostgreSQL\b', ['MySQL', 'MongoDB', 'SQLite']),
    (r'\bKafka\b', ['RabbitMQ', 'Pulsar', 'Redis Streams']),
    (r'\bPrometheus\b', ['Grafana', 'Datadog', 'Jaeger']),
    (r'\bJaeger\b', ['Prometheus', 'Zipkin', 'OpenTelemetry']),
    (r'\bOpenTelemetry\b', ['Prometheus', 'Jaeger', 'Zipkin']),

    # Role sequences (chat messages)
    (r'\bsystem, user, assistant\b', ['admin, client, server', 'input, process, output', 'master, worker, agent']),
    (r'\buser, assistant\b', ['client, server', 'input, output', 'prompt, response']),

    # -----------------------------------------------------------------------
    # Evaluation / observation
    # -----------------------------------------------------------------------
    (r'\bBLEU\b', ['ROUGE', 'METEOR', 'BERTScore']),
    (r'\bROUGE\b', ['BLEU', 'METEOR', 'BERTScore']),
    (r'\bBERTScore\b', ['BLEU', 'ROUGE', 'METEOR']),
    (r'\bF1\b', ['Precision', 'Recall', 'Accuracy']),

    # -----------------------------------------------------------------------
    # Quantization
    # -----------------------------------------------------------------------
    (r'\bINT4\b', ['INT8', 'FP16', 'FP32']),
    (r'\bINT8\b', ['INT4', 'FP16', 'FP32']),
    (r'\bFP16\b', ['INT8', 'INT4', 'BF16']),
    (r'\bBF16\b', ['FP16', 'INT8', 'FP32']),
    (r'\b4-bit\b', ['8-bit', '16-bit', '32-bit']),
    (r'\b8-bit\b', ['4-bit', '16-bit', '32-bit']),
    (r'\bPost-Training Quantization\b', ['Quantization-Aware Training', 'Dynamic Quantization', 'Mixed Precision']),

    # -----------------------------------------------------------------------
    # Agent / orchestration
    # -----------------------------------------------------------------------
    (r'\bOrchestrator\b', ['Executor', 'Router', 'Planner']),
    (r'\bSupervisor\b', ['Worker', 'Executor', 'Planner']),
    (r'\bReAct\b', ['Chain-of-Thought', 'Tree-of-Thought', 'Plan-and-Execute']),
    (r'\bChain-of-Thought\b', ['Tree-of-Thought', 'ReAct', 'Plan-and-Execute']),
    (r'\bTree-of-Thought\b', ['Chain-of-Thought', 'ReAct', 'Plan-and-Execute']),
    (r'\bSelf-Consistency\b', ['Chain-of-Thought', 'ReAct', 'Majority Voting']),
    (r'\bMajority Voting\b', ['Self-Consistency', 'Beam Search', 'Best-of-N']),

    # -----------------------------------------------------------------------
    # Data / storage / search
    # -----------------------------------------------------------------------
    (r'\bvector store\b', ['relational database', 'key-value store', 'graph database']),
    (r'\bvector database\b', ['relational database', 'key-value store', 'graph database']),
    (r'\bembedding\b', ['tokenization', 'quantization', 'normalization']),
    (r'\bembeddings\b', ['tokens', 'logits', 'activations']),
    (r'\bchunking\b', ['tokenization', 'summarization', 'indexing']),
    (r'\bHNSW\b', ['IVF', 'PQ', 'Flat Index']),
    (r'\bBM25\b', ['TF-IDF', 'Dense Retrieval', 'Sparse Retrieval']),
    (r'\bHybrid Search\b', ['Dense Search', 'Sparse Search', 'Keyword Search']),
    (r'\bReranker\b', ['Retriever', 'Embedder', 'Chunker']),

    # -----------------------------------------------------------------------
    # Cloud / infra
    # -----------------------------------------------------------------------
    (r'\bGCP Secret Manager\b', ['AWS Secrets Manager', 'HashiCorp Vault', 'Azure Key Vault']),
    (r'\bAWS Secrets Manager\b', ['GCP Secret Manager', 'HashiCorp Vault', 'Azure Key Vault']),
    (r'\bToken Bucket\b', ['Leaky Bucket', 'Fixed Window', 'Sliding Window']),
    (r'\bLeaky Bucket\b', ['Token Bucket', 'Fixed Window', 'Sliding Window']),

    # -----------------------------------------------------------------------
    # Vietnamese: directional / comparative
    # -----------------------------------------------------------------------
    (r'đầu tiên', ['cuối cùng', 'bất kỳ']),
    (r'cuối cùng', ['đầu tiên', 'ngẫu nhiên']),
    (r'token đầu tiên', ['token cuối cùng', 'toàn bộ token']),
    (r'cao nhất', ['thấp nhất', 'trung bình']),
    (r'thấp nhất', ['cao nhất', 'trung bình']),
    (r'lớn nhất', ['nhỏ nhất', 'trung bình']),
    (r'nhỏ nhất', ['lớn nhất', 'trung bình']),
    (r'nhiều nhất', ['ít nhất', 'trung bình']),
    (r'ít nhất', ['nhiều nhất', 'trung bình']),
    (r'cao hơn', ['thấp hơn', 'bằng']),
    (r'thấp hơn', ['cao hơn', 'bằng']),
    (r'lớn hơn', ['nhỏ hơn', 'bằng']),
    (r'nhỏ hơn', ['lớn hơn', 'bằng']),
    (r'nhanh hơn', ['chậm hơn', 'bằng nhau']),
    (r'chậm hơn', ['nhanh hơn', 'bằng nhau']),
    (r'nhiều hơn', ['ít hơn', 'bằng nhau']),
    (r'ít hơn', ['nhiều hơn', 'bằng nhau']),
    (r'tốt hơn', ['kém hơn', 'tương đương']),
    (r'kém hơn', ['tốt hơn', 'tương đương']),
    (r'tăng lên', ['giảm xuống', 'giữ nguyên']),
    (r'giảm xuống', ['tăng lên', 'giữ nguyên']),
    (r'tăng cường', ['giảm thiểu', 'duy trì']),
    (r'giảm thiểu', ['tăng cường', 'duy trì']),
    (r'(?<![a-zA-ZÀ-ɏ])tăng(?![a-zA-ZÀ-ɏ])', ['giảm', 'duy trì']),
    (r'(?<![a-zA-ZÀ-ɏ])giảm(?![a-zA-ZÀ-ɏ])', ['tăng', 'duy trì']),

    # -----------------------------------------------------------------------
    # Vietnamese: temporal
    # -----------------------------------------------------------------------
    (r'trước khi', ['sau khi', 'đồng thời khi']),
    (r'sau khi', ['trước khi', 'trong khi']),
    (r'(?<![a-zA-ZÀ-ɏ])trước(?![a-zA-ZÀ-ɏ])', ['sau', 'trong']),
    (r'(?<![a-zA-ZÀ-ɏ])sau(?![a-zA-ZÀ-ɏ])', ['trước', 'trong']),

    # -----------------------------------------------------------------------
    # Vietnamese: input/output
    # -----------------------------------------------------------------------
    (r'đầu vào', ['đầu ra', 'bộ nhớ đệm']),
    (r'đầu ra', ['đầu vào', 'bộ nhớ đệm']),
    (r'\binput\b', ['output', 'embedding']),
    (r'\boutput\b', ['input', 'embedding']),
    (r'nhận được', ['gửi đi', 'xử lý']),
    (r'gửi yêu cầu', ['nhận yêu cầu', 'xử lý yêu cầu']),

    # -----------------------------------------------------------------------
    # Vietnamese: modal / certainty
    # -----------------------------------------------------------------------
    (r'luôn luôn', ['đôi khi', 'không bao giờ']),
    (r'không bao giờ', ['luôn luôn', 'đôi khi']),
    (r'bắt buộc', ['tùy chọn', 'không cần thiết']),
    (r'tùy chọn', ['bắt buộc', 'không hỗ trợ']),
    (r'bắt buộc phải', ['không cần', 'có thể']),
    (r'không được phép', ['bắt buộc phải', 'có thể']),
    (r'tất định', ['ngẫu nhiên', 'xác suất']),
    (r'ngẫu nhiên', ['tất định', 'tuần tự']),

    # -----------------------------------------------------------------------
    # Vietnamese: process verbs
    # -----------------------------------------------------------------------
    (r'lấy mẫu từ', ['loại bỏ từ', 'giữ nguyên từ']),
    (r'giữ lại', ['loại bỏ', 'thay thế']),
    (r'loại bỏ', ['giữ lại', 'thêm vào']),
    (r'dừng', ['tiếp tục', 'bắt đầu']),
    (r'bắt đầu', ['dừng', 'tạm dừng']),
    (r'chuyển tiếp', ['giữ lại', 'loại bỏ']),
    (r'phân rã', ['tổng hợp', 'gộp lại']),
    (r'tóm tắt', ['mở rộng', 'sao chép']),
    (r'song song', ['tuần tự', 'đồng bộ']),
    (r'tuần tự', ['song song', 'ngẫu nhiên']),
    (r'đồng bộ', ['bất đồng bộ', 'song song']),
    (r'bất đồng bộ', ['đồng bộ', 'tuần tự']),
    (r'song song đồng thời', ['tuần tự từng bước', 'đồng bộ hoàn toàn']),

    # -----------------------------------------------------------------------
    # Vietnamese: probability / math concepts
    # -----------------------------------------------------------------------
    (r'xác suất tích lũy', ['xác suất đơn lẻ', 'xác suất tối đa']),
    (r'tích lũy', ['đơn lẻ', 'trung bình']),
    (r'xác suất cao nhất', ['xác suất thấp nhất', 'xác suất ngẫu nhiên']),
    (r'xác suất thấp nhất', ['xác suất cao nhất', 'xác suất trung bình']),
    (r'tổng xác suất', ['xác suất đơn lẻ', 'trung bình xác suất']),
    (r'đạt ngưỡng', ['không đạt ngưỡng', 'vượt ngưỡng']),
    (r'vượt ngưỡng', ['đạt ngưỡng', 'dưới ngưỡng']),
    (r'tổng số lượng', ['số lượng tối đa', 'số lượng tối thiểu']),
    (r'tối đa', ['tối thiểu', 'trung bình']),
    (r'tối thiểu', ['tối đa', 'trung bình']),

    # -----------------------------------------------------------------------
    # Vietnamese: error handling / reliability
    # -----------------------------------------------------------------------
    (r'bắt ngoại lệ', ['bỏ qua ngoại lệ', 'log và tiếp tục']),
    (r'Vượt quá giới hạn', ['Chưa đạt giới hạn', 'Đạt đúng giới hạn']),
    (r'chuyển sang Provider dự phòng', ['dừng hoàn toàn', 'thử lại vô hạn']),
    (r'tự động', ['thủ công', 'theo lịch']),
    (r'thủ công', ['tự động', 'theo lịch']),

    # -----------------------------------------------------------------------
    # Vietnamese: storage / memory management
    # -----------------------------------------------------------------------
    (r'Lưu trữ trong biến môi trường', ['Hardcode trực tiếp vào source code', 'Lưu vào file .env commit lên Git']),
    (r'inject vào container', ['hardcode vào image', 'lưu vào database']),
    (r'biến môi trường', ['biến toàn cục', 'file cấu hình']),

    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------
    # MIG / GPU slicing
    # -----------------------------------------------------------------------
    (r'\b7\b thực thể', ['4 thực thể', '2 thực thể', '14 thực thể']),

    # -----------------------------------------------------------------------
    # Vietnamese: negation / affirmation
    # -----------------------------------------------------------------------
    (r'không kèm theo', ['có kèm theo', 'bắt buộc kèm theo']),
    (r'kèm theo', ['không kèm theo', 'thay thế bằng']),
    (r'trực tiếp', ['gián tiếp', 'tuần tự']),
    (r'gián tiếp', ['trực tiếp', 'song song']),
    (r'phủ định', ['khẳng định', 'trung lập']),
    (r'khẳng định', ['phủ định', 'bác bỏ']),
    (r'ẩn', ['hiển thị', 'công khai']),
    (r'hiển thị', ['ẩn', 'mã hóa']),
    (r'tập trung vào', ['bỏ qua', 'phân tán qua']),
    (r'chú ý tốt nhất', ['chú ý kém nhất', 'chú ý đồng đều']),
    (r'bỏ sót', ['ghi nhớ', 'xử lý đúng']),
    (r'vô tình', ['cố ý', 'có chủ đích']),

    # -----------------------------------------------------------------------
    # Reasoning / prompt patterns
    # -----------------------------------------------------------------------
    (r'Thought -> Action -> Observation', ['Action -> Observation -> Thought', 'Observation -> Thought -> Action']),
    (r'Reasoning and Acting', ['Chain-of-Thought', 'Plan-and-Execute', 'Observe-and-Decide']),
    (r'Lập luận và Hành động', ['Quan sát và Phản hồi', 'Lập kế hoạch và Thực thi']),
    (r'step-by-step reasoning', ['end-to-end reasoning', 'parallel reasoning', 'direct answer']),
    (r'từng bước một', ['toàn bộ cùng lúc', 'ngẫu nhiên']),
    (r'lập luận trung gian', ['câu trả lời trực tiếp', 'phán đoán cuối cùng']),
    (r'bước lập luận', ['câu trả lời', 'kết luận']),
    (r'ranh giới quyết định', ['trung tâm phân phối', 'ngoại lệ']),
    (r'Edge cases', ['Common cases', 'Random cases', 'Simple cases']),

    # -----------------------------------------------------------------------
    # API / config params
    # -----------------------------------------------------------------------
    (r'\bresponse_format\b', ['output_format', 'json_mode', 'format_type']),
    (r'\bjson_object\b', ['json_array', 'plain_text', 'markdown']),
    (r'\bsystem_instruction\b', ['user_instruction', 'model_instruction', 'context']),
    (r'\bmax_tokens\b', ['min_tokens', 'total_tokens', 'context_tokens']),
    (r'\bstop_sequences\b', ['start_sequences', 'filter_sequences', 'control_sequences']),
    (r'\btool_choice\b', ['tool_mode', 'function_choice', 'agent_choice']),

    # -----------------------------------------------------------------------
    # Security / reliability patterns
    # -----------------------------------------------------------------------
    (r'Prompt Injection', ['Prompt Leaking', 'Jailbreaking', 'Data Poisoning']),
    (r'Jailbreaking', ['Prompt Injection', 'Prompt Leaking', 'Data Poisoning']),
    (r'Hallucination', ['Confabulation', 'Fabrication', 'Overfitting']),
    (r'độc hại', ['lành mạnh', 'trung tính']),
    (r'an toàn', ['nguy hiểm', 'không an toàn']),
    (r'kiểm duyệt', ['bỏ qua', 'tăng cường']),
    (r'dữ liệu bên ngoài', ['dữ liệu nội bộ', 'dữ liệu huấn luyện']),

    # -----------------------------------------------------------------------
    # Context window / memory
    # -----------------------------------------------------------------------
    (r'đầu \(Primacy effect\)', ['cuối (Recency effect)', 'giữa (Middle effect)']),
    (r'cuối \(Recency effect\)', ['đầu (Primacy effect)', 'giữa (Middle effect)']),
    (r'Primacy effect', ['Recency effect', 'Middle bias', 'Uniform attention']),
    (r'Recency effect', ['Primacy effect', 'Middle bias', 'Uniform attention']),
    (r'context window', ['training window', 'inference window', 'attention window']),
    (r'cửa sổ ngữ cảnh', ['kích thước batch', 'độ dài prompt', 'bộ nhớ mô hình']),

    # -----------------------------------------------------------------------
    # Templating / markup
    # -----------------------------------------------------------------------
    (r'Jinja2', ['Mako', 'Handlebars', 'Mustache']),
    (r'thẻ XML', ['thẻ HTML', 'thẻ JSON', 'thẻ Markdown']),
    (r'Markdown', ['reStructuredText', 'AsciiDoc', 'HTML']),
    (r'Persona', ['Agent', 'Character', 'Role']),
    (r'ràng buộc bảo mật', ['ràng buộc hiệu suất', 'ràng buộc định dạng']),

    # -----------------------------------------------------------------------
    # LLM concepts
    # -----------------------------------------------------------------------
    (r'Logarit xác suất', ['Tổng xác suất', 'Trung bình xác suất', 'Entropy xác suất']),
    (r'\bLogprob\b', ['Perplexity', 'Entropy', 'Confidence Score']),
    (r'\blogprob\b', ['perplexity', 'entropy', 'confidence']),
    (r'Classifier/SLM', ['LLM/Embedder', 'Vector Store/Index', 'Reranker/Scorer']),
    (r'đánh giá độ phức tạp', ['đánh giá độ chính xác', 'đánh giá tốc độ']),
    (r'câu hỏi dễ', ['câu hỏi khó', 'câu hỏi ngẫu nhiên']),
    (r'model rẻ', ['model đắt', 'model chậm']),

    # -----------------------------------------------------------------------
    # Token count with SI suffixes
    # -----------------------------------------------------------------------
    (r'\b200M\b', ['100M', '500M', '1B']),
    (r'\b100M\b', ['200M', '500M', '1B']),
    (r'\b1B\b', ['500M', '100M', '10B']),
    (r'\b128K\b', ['64K', '256K', '32K']),
    (r'\b64K\b', ['128K', '32K', '256K']),
    (r'\b32K\b', ['64K', '128K', '16K']),
    (r'\b16K\b', ['32K', '8K', '64K']),
    (r'\b8K\b', ['16K', '4K', '32K']),
    (r'\b4K\b', ['8K', '2K', '16K']),

    # -----------------------------------------------------------------------
    # Agent / tool behavior
    # -----------------------------------------------------------------------
    (r'nhiều nhánh', ['một nhánh', 'ít nhánh']),
    (r'trạng thái trung gian', ['kết quả cuối cùng', 'đầu vào ban đầu']),
    (r'môi trường bên ngoài', ['hệ thống nội bộ', 'bộ nhớ cục bộ']),
    (r'tương tác với môi trường', ['hoạt động độc lập', 'chỉ đọc ngữ cảnh']),
    (r'Tool Registry', ['Model Registry', 'Prompt Library', 'Knowledge Base']),
    (r'Tool Arguments', ['Tool Results', 'Tool Errors', 'Tool Metadata']),
    (r'Tool Name', ['Tool ID', 'Tool Version', 'Tool Schema']),
    (r'bịa ra', ['tìm thấy đúng', 'chọn chính xác']),
    (r'không hề tồn tại', ['đã tồn tại', 'vẫn còn tồn tại']),
    (r'thất bại', ['thành công', 'không xác định']),
    (r'lỗi', ['kết quả', 'thành công']),
    (r'sai', ['đúng', 'không xác định']),
    (r'truy vấn', ['ghi', 'cập nhật', 'xóa']),
    (r'chỉ đọc', ['đọc và ghi', 'chỉ ghi']),
    (r'không ghi', ['có ghi', 'tự động ghi']),
    (r'liên tục gọi', ['gọi một lần', 'không gọi']),
    (r'cùng một tham số', ['tham số khác nhau', 'không có tham số']),
    (r'Root Cause Analysis', ['Performance Analysis', 'Cost Analysis', 'Latency Analysis']),
    (r'Debugging', ['Monitoring', 'Logging', 'Tracing']),
    (r'phân tích nguyên nhân gốc rễ', ['phân tích hiệu suất', 'phân tích chi phí']),

    # -----------------------------------------------------------------------
    # Evaluation benchmarks
    # -----------------------------------------------------------------------
    (r'\bSWE-bench\b', ['HumanEval', 'MBPP', 'LiveCodeBench']),
    (r'\bGAIA\b', ['AgentBench', 'ToolBench', 'TaskBench']),
    (r'\bToolBench\b', ['GAIA', 'AgentBench', 'SWE-bench']),
    (r'\bHumanEval\b', ['MBPP', 'SWE-bench', 'LiveCodeBench']),

    # -----------------------------------------------------------------------
    # Memory / reflection patterns (Reflexion, MemGPT, etc.)
    # -----------------------------------------------------------------------
    (r'Reflections', ['Memories', 'Knowledge', 'Observations']),
    (r'tự đánh giá', ['đánh giá ngoài', 'không đánh giá']),
    (r'lần thử thất bại', ['lần thử thành công', 'lần thử đầu tiên']),
    (r'bài học rút ra', ['quy trình chuẩn', 'kết quả ban đầu']),
    (r'Observation', ['Action', 'Thought', 'Result']),
    (r'Action', ['Observation', 'Thought', 'Decision']),

    # -----------------------------------------------------------------------
    # Function / tool schema
    # -----------------------------------------------------------------------
    (r'\bOptional\[str\]\b', ['Required[str]', 'Optional[int]', 'List[str]']),
    (r'giá trị mặc định', ['giá trị bắt buộc', 'không có giá trị']),
    (r'NÊN dùng', ['KHÔNG NÊN dùng', 'CÓ THỂ dùng']),
    (r'KHÔNG NÊN dùng', ['NÊN dùng', 'BẮT BUỘC dùng']),

    # -----------------------------------------------------------------------
    # Tree-of-Thought specific
    # -----------------------------------------------------------------------
    (r'khám phá nhiều nhánh', ['đi theo một nhánh', 'bỏ qua tất cả nhánh']),
    (r'đánh giá các trạng thái', ['bỏ qua các trạng thái', 'chọn ngẫu nhiên trạng thái']),
    (r'backtracking', ['forward search', 'greedy search', 'random walk']),

    # -----------------------------------------------------------------------
    # Few-shot / prompt patterns
    # -----------------------------------------------------------------------
    (r'không kèm theo bất kỳ ví dụ', ['kèm theo nhiều ví dụ', 'kèm theo một ví dụ']),
    (r'ví dụ minh họa', ['hướng dẫn', 'ràng buộc', 'context']),
    (r'Zero-shot', ['One-shot', 'Few-shot', 'Chain-of-Thought']),
    (r'Few-shot', ['Zero-shot', 'One-shot', 'Zero-shot CoT']),
    (r'One-shot', ['Zero-shot', 'Few-shot', 'Many-shot']),

    # -----------------------------------------------------------------------
    # Format / output
    # -----------------------------------------------------------------------
    (r'Cắt bỏ', ['Thêm vào', 'Giữ nguyên']),
    (r'loại bỏ', ['thêm vào', 'giữ nguyên']),
    (r'chuỗi JSON thuần túy', ['chuỗi Markdown', 'XML thuần túy', 'plain text']),
    (r'Markdown codeblock', ['JSON wrapper', 'XML wrapper', 'HTML wrapper']),
    (r'fence', ['tag', 'delimiter', 'separator']),
]

NUM_SCALE = [0.5, 2.0, 10.0, 0.1]  # multipliers for number mutation

# Hardcoded wrong values for important domain constants
_DOMAIN_WRONG = {
    '0.0': ['1.0', '0.5', '2.0'],
    '1.0': ['0.0', '0.5', '2.0'],
    '0.5': ['0.0', '1.0', '2.0'],
    '0': ['1', '2', '10'],
    '1': ['0', '2', '10'],
    '7': ['4', '2', '14'],  # MIG instances
    '10': ['5', '50', '100'],
    '100': ['50', '1000', '10'],
    '50': ['25', '100', '10'],
}


def _number_variants(num_str):
    """Return up to 3 different wrong number strings for a given match."""
    # Check domain constants first
    if num_str in _DOMAIN_WRONG:
        return _DOMAIN_WRONG[num_str]

    clean = num_str.replace(',', '')
    try:
        val = float(clean)
    except ValueError:
        return []

    # Special case: zero * anything = zero, use additive offsets instead
    if val == 0.0:
        wrong_vals = [1.0, 0.5, -1.0]
    else:
        wrong_vals = [val * s for s in NUM_SCALE if val * s != val]

    results = []
    for wrong_val in wrong_vals:
        if wrong_val == val:
            continue
        # Preserve decimal style of original
        has_dot = '.' in num_str
        if not has_dot and wrong_val == int(wrong_val):
            formatted = f'{int(wrong_val):,}'
        elif has_dot:
            # Keep same number of decimal places as original
            decimals = len(num_str.rstrip('0').split('.')[-1]) if '.' in num_str else 1
            formatted = f'{wrong_val:.{decimals}f}'.rstrip('0').rstrip('.')
            if '.' in num_str and '.' not in formatted:
                formatted += '.0'
        else:
            formatted = f'{wrong_val:g}'
        if formatted != num_str and formatted not in results:
            results.append(formatted)
        if len(results) >= 3:
            break
    return results


def generate_mutations(text):
    """Apply all mutation rules to text. Return list of unique mutated strings."""
    candidates = []
    seen = {text}

    # Term swap rules
    for pattern, replacements in TERM_RULES:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            matched_text = m.group(0)
            for rep in replacements:
                # Skip if replacement already appears elsewhere in the text
                # (avoids "đầu ra và đầu ra" type redundancy)
                rest = text[:m.start()] + text[m.end():]
                if rep.lower() in rest.lower() and rep.lower() != matched_text.lower():
                    continue
                mutated = text[:m.start()] + rep + text[m.end():]
                if mutated not in seen:
                    seen.add(mutated)
                    candidates.append(mutated)

    # Number mutation — only on numbers not inside backtick formulas (those handled by term rules above)
    # Find numbers in plain text portions
    num_pat = re.compile(r'\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b|\b\d+(?:\.\d+)?\b')
    for m in num_pat.finditer(text):
        # Skip if inside backtick block
        before = text[:m.start()]
        if before.count('`') % 2 == 1:
            continue
        for wrong_num in _number_variants(m.group()):
            mutated = text[:m.start()] + wrong_num + text[m.end():]
            if mutated not in seen:
                seen.add(mutated)
                candidates.append(mutated)

    return candidates


def jaccard_similarity(a, b):
    """Token-level Jaccard similarity between two strings."""
    sa = set(re.findall(r'\w+', a.lower()))
    sb = set(re.findall(r'\w+', b.lower()))
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / len(sa | sb)


def pick_distractors(correct, candidates, n=3, rng=None):
    """Pick n diverse distractors from candidates, all different from correct."""
    if rng is None:
        rng = random.Random(42)
    selected = []
    seen = {correct}
    for c in candidates:
        c = c.strip()
        if not c or c in seen:
            continue
        # Not too similar to already-selected distractors
        too_close = any(jaccard_similarity(c, s) > 0.85 for s in selected)
        if too_close:
            continue
        seen.add(c)
        selected.append(c)
        if len(selected) >= n:
            break
    return selected


def build_day_pool(questions):
    """Group correct answers by day for cross-day fallback."""
    pool = defaultdict(list)
    for q in questions:
        pool[q['day']].append((q['id'], q['correct_answer']))
    return pool


def fallback_distractors(q, day_pool, needed, rng):
    """
    Fill missing distractor slots from same-day correct answers,
    filtering by Jaccard similarity against the correct answer.
    """
    correct = q['correct_answer']
    day = q['day']
    candidates = [(qid, ans) for qid, ans in day_pool[day] if qid != q['id']]
    rng.shuffle(candidates)
    result = []
    seen = {correct}
    for _, ans in candidates:
        ans = ans.strip()
        if not ans or ans in seen:
            continue
        if jaccard_similarity(ans, correct) > 0.65:
            continue
        seen.add(ans)
        result.append(ans)
        if len(result) >= needed:
            break
    return result


def regenerate_question(q, day_pool, rng):
    """Regenerate distractors for one question. Returns modified copy."""
    correct = q['correct_answer']
    mutations = generate_mutations(correct)
    distractors = pick_distractors(correct, mutations, n=3, rng=rng)

    # Fill remaining slots from same-day pool if needed
    if len(distractors) < 3:
        extra = fallback_distractors(q, day_pool, 3 - len(distractors), rng)
        distractors.extend(extra)

    # If still not enough (very rare), keep original wrong options
    original_wrong = [o for o in q['options'] if o != correct]
    while len(distractors) < 3:
        for w in original_wrong:
            if w not in distractors and w != correct:
                distractors.append(w)
                if len(distractors) >= 3:
                    break

    distractors = distractors[:3]

    # Build new options list and shuffle
    new_options = [correct] + distractors
    rng.shuffle(new_options)
    correct_index = new_options.index(correct)

    new_q = dict(q)
    new_q['options'] = new_options
    new_q['correct_index'] = correct_index
    new_q['correct_answer'] = correct
    return new_q


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base, 'data', 'questions.json')

    with open(data_path, encoding='utf-8') as f:
        questions = json.load(f)

    print(f'Loaded {len(questions)} questions')

    rng = random.Random(2024)
    day_pool = build_day_pool(questions)

    new_questions = []
    mutated_count = 0
    fallback_count = 0

    for q in questions:
        correct = q['correct_answer']
        mutations = generate_mutations(correct)
        distractors = pick_distractors(correct, mutations, n=3, rng=rng)

        used_fallback = len(distractors) < 3
        if used_fallback:
            extra = fallback_distractors(q, day_pool, 3 - len(distractors), rng)
            distractors.extend(extra)
            fallback_count += 1

        original_wrong = [o for o in q['options'] if o != correct]
        while len(distractors) < 3:
            for w in original_wrong:
                if w not in distractors and w != correct:
                    distractors.append(w)
                    if len(distractors) >= 3:
                        break

        distractors = distractors[:3]
        new_options = [correct] + distractors
        rng.shuffle(new_options)
        correct_index = new_options.index(correct)

        new_q = dict(q)
        new_q['options'] = new_options
        new_q['correct_index'] = correct_index
        new_q['correct_answer'] = correct

        if new_q['options'] != q['options']:
            mutated_count += 1

        new_questions.append(new_q)

    print(f'  Changed options: {mutated_count} questions')
    print(f'  Used fallback (same-day pool): {fallback_count} questions')

    # Verify
    mismatches = sum(
        1 for q in new_questions
        if q['options'][q['correct_index']] != q['correct_answer']
    )
    print(f'  Answer mismatches: {mismatches}')

    # Show examples
    print('\n=== Sample regenerated questions ===')
    shown = 0
    for orig, new in zip(questions, new_questions):
        if orig['options'] != new['options'] and shown < 5:
            print(f'Q: {orig["question"][:70]}')
            print(f'  correct: {new["correct_answer"][:80]}')
            for o in new['options']:
                mark = '✓' if o == new['correct_answer'] else '✗'
                print(f'  {mark} {o[:80]}')
            print()
            shown += 1

    # Save to all paths
    paths = [
        os.path.join(base, 'data', 'questions.json'),
        os.path.join(base, 'static', 'data', 'questions.json'),
        os.path.join(base, 'api', 'data', 'questions.json'),
    ]
    for p in paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(new_questions, f, ensure_ascii=False, indent=2)
        size_kb = os.path.getsize(p) / 1024
        print(f'  Saved: {p} ({size_kb:.0f} KB)')


if __name__ == '__main__':
    main()
