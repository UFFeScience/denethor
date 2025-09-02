import os
import json
import glob
import numpy as np

def remove_outliers_std(data, threshold=3):
    if len(data) < 2:
        return data, []
    mean = np.mean(data)
    std = np.std(data)
    filtered = [x for x in data if abs(x - mean) <= threshold * std]
    outliers = [x for x in data if abs(x - mean) > threshold * std]
    return filtered, outliers

def aggregate_metrics_by_filename(pattern, duration_key, size_key):
    # Dicionário: nome_arquivo -> lista de bps
    file_throughputs = {}
    for file in glob.glob(pattern):
        with open(file, "r") as f:
            data = json.load(f)
        if "files" in data:
            for item in data["files"]:
                duration = item.get(duration_key)
                size = item.get(size_key)
                filename = item.get("file_name") or item.get("filename")
                if duration and size and filename:
                    # bytes/ms -> bits/s
                    bps = (size * 8) / (duration / 1000)
                    if filename not in file_throughputs:
                        file_throughputs[filename] = []
                    file_throughputs[filename].append(bps)
    return file_throughputs

def compute_stats(file_throughputs):
    stats = []
    all_tps = []
    outlier_info = {}
    for filename, tps in file_throughputs.items():
        if tps:
            filtered, outliers = remove_outliers_std(tps)
            outlier_info[filename] = outliers
            if filtered:
                stats.append({
                    "file": filename,
                    "avg": np.mean(filtered),
                    "std": np.std(filtered),
                    "median": np.median(filtered),
                    "min": np.min(filtered),
                    "max": np.max(filtered),
                    "count": len(filtered),
                    "outliers": len(outliers)
                })
                all_tps.extend(filtered)
    return stats, all_tps, outlier_info

def compute_general_stats(all_tps):
    if not all_tps:
        return None
    return {
        "avg": np.mean(all_tps),
        "std": np.std(all_tps),
        "median": np.median(all_tps),
        "min": np.min(all_tps),
        "max": np.max(all_tps),
        "count": len(all_tps)
    }

def print_stats(stats, all_tps, tipo, geral=None):
    print(f"\nEstatísticas para {tipo} (sem outliers):")
    for s in stats:
        print(
            f"{s['file']}: média={s['avg']:.2f} bps, std={s['std']:.2f}, mediana={s['median']:.2f}, "
            f"min={s['min']:.2f}, max={s['max']:.2f}, n={s['count']}, outliers={s['outliers']}"
        )
    if geral:
        print(
            f"GERAL: média={geral['avg']:.2f} bps, std={geral['std']:.2f}, mediana={geral['median']:.2f}, "
            f"min={geral['min']:.2f}, max={geral['max']:.2f}, n={geral['count']}"
        )
    else:
        print("Nenhum dado encontrado.")

def save_stats_to_txt(stats, geral, tipo, output_path):
    with open(output_path, "w") as f:
        f.write(f"Estatísticas para {tipo} (sem outliers):\n")
        for s in stats:
            f.write(
                f"{s['file']}: média={s['avg']:.2f} bps, std={s['std']:.2f}, mediana={s['median']:.2f}, "
                f"min={s['min']:.2f}, max={s['max']:.2f}, n={s['count']}, outliers={s['outliers']}\n"
            )
        if geral:
            f.write(
                f"GERAL: média={geral['avg']:.2f} bps, std={geral['std']:.2f}, mediana={geral['median']:.2f}, "
                f"min={geral['min']:.2f}, max={geral['max']:.2f}, n={geral['count']}\n"
            )
        else:
            f.write("Nenhum dado encontrado.\n")

if __name__ == "__main__":
    log_dir = "src/file_metrics/lambda/logs"
    download_file_tps = aggregate_metrics_by_filename(
        os.path.join(log_dir, "*_download_metrics.json"),
        "download_duration_ms", "file_size"
    )
    upload_file_tps = aggregate_metrics_by_filename(
        os.path.join(log_dir, "*_upload_metrics.json"),
        "upload_duration_ms", "file_size"
    )
    download_stats, download_tps, download_outliers = compute_stats(download_file_tps)
    upload_stats, upload_tps, upload_outliers = compute_stats(upload_file_tps)
    download_geral = compute_general_stats(download_tps)
    upload_geral = compute_general_stats(upload_tps)
    print_stats(download_stats, download_tps, "DOWNLOAD", download_geral)
    print_stats(upload_stats, upload_tps, "UPLOAD", upload_geral)

    # Salvar em arquivos texto
    save_stats_to_txt(
        download_stats, download_geral, "DOWNLOAD",
        os.path.join(log_dir, "download_stats.txt")
    )
    save_stats_to_txt(
        upload_stats, upload_geral, "UPLOAD",
        os.path.join(log_dir, "upload_stats.txt")
    )