interface ModelBadgeProps {
  modelInfo?: string;
}

export default function ModelBadge({ modelInfo }: ModelBadgeProps) {
  if (!modelInfo) {
    return (
      <span className="px-2 py-1 bg-gray-200 text-gray-700 rounded-full text-xs font-medium">
        Default
      </span>
    );
  }

  const modelInfoLower = modelInfo.toLowerCase();

  if (modelInfoLower.includes('anthropic') || modelInfoLower.includes('claude')) {
    return (
      <span className="px-2 py-1 bg-purple-500 text-white rounded-full text-xs font-medium" title={modelInfo}>
        Claude
      </span>
    );
  } else if (modelInfoLower.includes('openai') || modelInfoLower.includes('gpt')) {
    return (
      <span className="px-2 py-1 bg-green-600 text-white rounded-full text-xs font-medium" title={modelInfo}>
        GPT
      </span>
    );
  } else {
    return (
      <span className="px-2 py-1 bg-gray-600 text-white rounded-full text-xs font-medium" title={modelInfo}>
        AI
      </span>
    );
  }
} 