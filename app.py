import os
import sys
import threading
import time
import random
import webbrowser
from tkinter import filedialog, messagebox
import customtkinter as ctk
import yt_dlp

# Configuração visual padrão
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class YouTubeAudioExtractor(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Extrator de Áudio YouTube (MP3) - Dacweb Soluções em TI")
        self.geometry("700x620")
        self.minsize(600, 570)

        # Variáveis de controle
        self.output_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self.is_downloading = False

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Área de inserção de URLs
        lbl_urls = ctk.CTkLabel(
            self, 
            text="Cole as URLs do YouTube (uma por linha):", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        lbl_urls.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        self.txt_urls = ctk.CTkTextbox(self, height=180, font=ctk.CTkFont(size=13))
        self.txt_urls.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")

        # 2. Painel de Configurações (Qualidade e Destino)
        frame_config = ctk.CTkFrame(self)
        frame_config.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        frame_config.grid_columnconfigure(1, weight=1)

        # Seletor de Qualidade
        lbl_quality = ctk.CTkLabel(frame_config, text="Qualidade MP3:")
        lbl_quality.grid(row=0, column=0, padx=15, pady=12, sticky="w")

        self.cmb_quality = ctk.CTkOptionMenu(
            frame_config, 
            values=["Alta (320 kbps)", "Média (192 kbps)", "Baixa (128 kbps)"]
        )
        self.cmb_quality.set("Alta (320 kbps)")
        self.cmb_quality.grid(row=0, column=1, padx=15, pady=12, sticky="w")

        # Seletor de Pasta de Destino
        lbl_folder = ctk.CTkLabel(frame_config, text="Salvar em:")
        lbl_folder.grid(row=1, column=0, padx=15, pady=(0, 12), sticky="w")

        self.lbl_path = ctk.CTkLabel(
            frame_config, 
            text=self.output_dir, 
            text_color="gray", 
            anchor="w"
        )
        self.lbl_path.grid(row=1, column=1, padx=15, pady=(0, 12), sticky="ew")

        btn_folder = ctk.CTkButton(
            frame_config, 
            text="Alterar Pasta", 
            width=110, 
            command=self._select_folder
        )
        btn_folder.grid(row=1, column=2, padx=15, pady=(0, 12))

        # 3. Progresso e Botão de Ação
        self.lbl_status = ctk.CTkLabel(self, text="Pronto para iniciar.", font=ctk.CTkFont(size=12))
        self.lbl_status.grid(row=3, column=0, padx=20, pady=(5, 0), sticky="w")

        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        self.progress_bar.set(0)

        self.btn_download = ctk.CTkButton(
            self, 
            text="Extrair MP3 em Lote", 
            height=45, 
            font=ctk.CTkFont(size=15, weight="bold"), 
            command=self._start_download_thread
        )
        self.btn_download.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        # 4. Console de Log
        self.txt_log = ctk.CTkTextbox(
            self, 
            height=110, 
            state="disabled", 
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.txt_log.grid(row=6, column=0, padx=20, pady=(5, 5), sticky="ew")

        # 5. Rodapé de Créditos com Link Clicável
        self.lbl_footer = ctk.CTkLabel(
            self,
            text="Desenvolvido por Douglas - Dacweb Soluções em TI",
            font=ctk.CTkFont(size=12, weight="bold", underline=True),
            text_color=("#1f538d", "#3a7ebf"),
            cursor="hand2"
        )
        self.lbl_footer.grid(row=7, column=0, padx=20, pady=(2, 12), sticky="e")
        
        # Eventos de clique e hover no rodapé
        self.lbl_footer.bind("<Button-1>", lambda e: webbrowser.open("https://dacweb.com.br"))
        self.lbl_footer.bind("<Enter>", lambda e: self.lbl_footer.configure(text_color=("#14375e", "#6ab0f3")))
        self.lbl_footer.bind("<Leave>", lambda e: self.lbl_footer.configure(text_color=("#1f538d", "#3a7ebf")))

    def _select_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_dir)
        if folder:
            self.output_dir = folder
            self.lbl_path.configure(text=self.output_dir)

    def _log(self, message):
        def _append():
            self.txt_log.configure(state="normal")
            self.txt_log.insert("end", f"{message}\n")
            self.txt_log.see("end")
            self.txt_log.configure(state="disabled")
        self.after(0, _append)

    def _update_status(self, text, progress=None):
        def _upd():
            self.lbl_status.configure(text=text)
            if progress is not None:
                self.progress_bar.set(progress)
        self.after(0, _upd)

    def _get_ffmpeg_path(self):
        """Localiza o FFmpeg embutido pelo PyInstaller ou na pasta local."""
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        local_ffmpeg = os.path.join(base_path, "ffmpeg.exe")
        if os.path.exists(local_ffmpeg):
            return base_path
        return None

    def _start_download_thread(self):
        if self.is_downloading:
            return

        raw_text = self.txt_urls.get("1.0", "end").strip()
        urls = [line.strip() for line in raw_text.splitlines() if line.strip()]

        if not urls:
            messagebox.showwarning("Aviso", "Insira pelo menos uma URL válida.")
            return

        self.is_downloading = True
        self.btn_download.configure(state="disabled", text="Processando Fila...")
        self.progress_bar.set(0)
        
        threading.Thread(target=self._download_worker, args=(urls,), daemon=True).start()

    def _download_worker(self, urls):
        quality_selection = self.cmb_quality.get()
        if "320" in quality_selection:
            bitrate = "320"
        elif "192" in quality_selection:
            bitrate = "192"
        else:
            bitrate = "128"

        ffmpeg_loc = self._get_ffmpeg_path()
        total = len(urls)
        sucessos = 0

        self._log(f"--- Iniciando lote de {total} vídeo(s) | Qualidade: {bitrate}kbps ---")

        for idx, url in enumerate(urls, start=1):
            self._log(f"[{idx}/{total}] Analisando: {url}")
            self._update_status(f"Baixando item {idx} de {total}...", 0)

            def progress_hook(d):
                if d['status'] == 'downloading':
                    total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                    downloaded = d.get('downloaded_bytes', 0)
                    if total_bytes:
                        pct = downloaded / total_bytes
                        self._update_status(
                            f"Item [{idx}/{total}] Baixando: {pct*100:.1f}%", 
                            pct
                        )
                elif d['status'] == 'finished':
                    self._update_status(
                        f"Item [{idx}/{total}] Convertendo para MP3 (aguarde)...", 
                        1.0
                    )

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': bitrate,
                }],
                'progress_hooks': [progress_hook],
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
            }

            if ffmpeg_loc:
                ydl_opts['ffmpeg_location'] = ffmpeg_loc

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                self._log(f"✔ [{idx}/{total}] Concluído com sucesso.")
                sucessos += 1
            except Exception as e:
                self._log(f"✖ [{idx}/{total}] Erro: {str(e)}")

            if idx < total:
                pause = random.uniform(2.0, 4.5)
                self._log(f"Aguardando {pause:.1f}s para evitar bloqueio do YouTube...")
                time.sleep(pause)

        self._update_status(f"Processo finalizado! ({sucessos}/{total} concluídos)", 1.0)
        self._log("=== Lote finalizado ===")
        
        def _reset_btn():
            self.is_downloading = False
            self.btn_download.configure(state="normal", text="Extrair MP3 em Lote")
            messagebox.showinfo(
                "Concluído", 
                f"Processamento finalizado!\n\nSucessos: {sucessos} de {total}\nPasta: {self.output_dir}"
            )
        self.after(0, _reset_btn)

if __name__ == "__main__":
    app = YouTubeAudioExtractor()
    app.mainloop()