import ReactMarkdown from "react-markdown";

export interface MarkdownContentProps {
  content: string;
  className?: string;
}

/**
 * Normalizes clinical LLM and template text into compliant Markdown:
 * 1. Converts unicode bullets (•, ●, etc.) at line starts into standard markdown list syntax ("- ").
 * 2. Un-merges inline bullets (e.g., "Alternative: • Paracetamol") into structured line breaks.
 * 3. Enforces double newlines after bolded subheadings (e.g. "**Why is it dangerous?**\nText")
 *    so CommonMark creates distinct paragraph blocks instead of soft-wrapping inline.
 * 4. Ensures list blocks are preceded by an empty line so CommonMark triggers <ul>/<ol>.
 */
function normalizeMarkdown(text: string): string {
  if (!text) return "";

  return text
    // Replace unicode bullets (•, ●, ○) at line starts with markdown "- "
    .replace(/^[•●○]\s*/gm, "- ")
    // Convert inline bullets (e.g. "Safe Alternative: • Paracetamol") into a clean list break
    .replace(/:\s*[•●○]\s*/g, ":\n\n- ")
    // Convert any remaining mid-text bullets preceded by whitespace
    .replace(/(\n|\.)\s*[•●○]\s*/g, "$1\n- ")
    // Ensure section subheadings like "**Why is it dangerous?**\nText" have a double newline
    .replace(/^(\*\*[^*]+?\*\*[:?]?)\s*\n([^\n\s])/gm, "$1\n\n$2")
    // Ensure lists preceded by a paragraph have a clean blank line
    .replace(/([^\n])\n([ \t]*[-*]\s)/g, "$1\n\n$2")
    .replace(/([^\n])\n([ \t]*\d+\.\s)/g, "$1\n\n$2");
}

export default function MarkdownContent({
  content,
  className = "",
}: MarkdownContentProps) {
  const normalized = normalizeMarkdown(content);

  return (
    <div className={`prose-sm max-w-none text-xs sm:text-sm leading-relaxed ${className}`}>
      <ReactMarkdown
        components={{
          p: ({ children }) => (
            <p className="mb-3 last:mb-0 leading-relaxed">{children}</p>
          ),
          strong: ({ children }) => (
            <strong className="font-bold tracking-tight text-inherit">{children}</strong>
          ),
          em: ({ children }) => (
            <em className="italic opacity-90">{children}</em>
          ),
          ul: ({ children }) => (
            <ul className="list-disc pl-5 my-2.5 space-y-1.5">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal pl-5 my-2.5 space-y-1.5">{children}</ol>
          ),
          li: ({ children }) => (
            <li className="leading-relaxed pl-1">{children}</li>
          ),
          h1: ({ children }) => (
            <h1 className="font-bold text-base my-2.5">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="font-bold text-sm sm:text-base my-2">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="font-bold text-xs sm:text-sm my-1.5">{children}</h3>
          ),
        }}
      >
        {normalized}
      </ReactMarkdown>
    </div>
  );
}
