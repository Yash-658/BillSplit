import { ImagePlus, X, ArrowRight, FileImage } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { extractBill } from "../api";
import type { Bill } from "../types";

type Preview = { id: string; file: File; name: string; url: string };

export function UploadScreen({ onExtracted }: { onExtracted: (bill: Bill) => void }) {
  const [previews, setPreviews] = useState<Preview[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const previewsRef = useRef<Preview[]>([]);

  function addFiles(files: FileList | null) {
    if (!files) return;
    const next = Array.from(files).map((file, index) => ({ id: `${file.name}-${file.lastModified}-${index}`, file, name: file.name, url: URL.createObjectURL(file) }));
    setPreviews((current) => [...current, ...next]);
  }

  async function continueToReview() {
    if (!previews.length || loading) return;
    setLoading(true);
    setError(null);
    try {
      onExtracted(await extractBill(previews.map((preview) => preview.file)));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Bill extraction failed.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    previewsRef.current = previews;
  }, [previews]);

  useEffect(() => {
    return () => {
      previewsRef.current.forEach((preview) => URL.revokeObjectURL(preview.url));
    };
  }, []);

  function remove(id: string) {
    const preview = previews.find((candidate) => candidate.id === id);
    if (preview) URL.revokeObjectURL(preview.url);
    setPreviews((current) => current.filter((preview) => preview.id !== id));
  }

  return (
    <section className="mx-auto max-w-3xl">
      <div className="mb-8 text-center">
        <p className="mb-3 text-sm font-bold uppercase tracking-[0.2em] text-coral">Split the bill, simply</p>
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">Start with a photo of your bill.</h1>
        <p className="mx-auto mt-4 max-w-xl text-slate-500">Upload one or more clear photos. We&apos;ll help you review every number before anyone pays.</p>
      </div>
      <div className="panel p-5 sm:p-8">
        <button type="button" onClick={() => inputRef.current?.click()} className="flex w-full flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50 px-5 py-12 transition hover:border-coral hover:bg-orange-50/30">
          <span className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-orange-100 text-coral"><ImagePlus size={26} /></span>
          <span className="font-semibold">Choose bill photos</span>
          <span className="mt-1 text-sm text-slate-500">JPG, PNG or WebP · one or multiple pages</span>
        </button>
        <input ref={inputRef} className="hidden" type="file" accept="image/jpeg,image/png,image/webp" multiple onChange={(event) => addFiles(event.target.files)} />
        {previews.length > 0 ? (
          <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3">
            {previews.map((preview) => (
              <div className="group relative overflow-hidden rounded-xl border border-slate-200" key={preview.id}>
                <img src={preview.url} alt={preview.name} className="h-36 w-full object-cover" />
                <button type="button" onClick={() => remove(preview.id)} aria-label={`Remove ${preview.name}`} className="absolute right-2 top-2 rounded-full bg-ink/80 p-1.5 text-white opacity-0 transition group-hover:opacity-100"><X size={14} /></button>
                <p className="truncate px-3 py-2 text-xs text-slate-500">{preview.name}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="mt-6 flex items-center justify-center gap-2 text-sm text-slate-400"><FileImage size={16} /> No photos selected yet</div>
        )}
        {error && <p role="alert" className="mt-5 rounded-xl bg-red-50 p-3 text-sm font-medium text-red-700">{error}</p>}
        <button type="button" onClick={continueToReview} disabled={!previews.length || loading} className="button-primary mt-8 w-full sm:w-auto sm:float-right disabled:cursor-not-allowed disabled:opacity-50">{loading ? "Extracting bill..." : <>Continue <ArrowRight size={17} /></>}</button>
        <div className="clear-both" />
      </div>
    </section>
  );
}
