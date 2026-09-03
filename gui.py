import argparse
import threading

import customtkinter as ctk

import main as core


class AutoRewardsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("auto-rewards")
        self.geometry("480x410")
        self.resizable(False, False)

        self.cancel_event = None
        self.worker = None
        self.search_count = 0

        self.searches_var = ctk.StringVar()
        self.delay_var = ctk.StringVar()
        self.browser_var = ctk.StringVar(value="Unknown")
        self.session_var = ctk.StringVar(value="Unknown")
        self.status_var = ctk.StringVar(value="Ready")

        self._build_widgets()
        self._load_initial_values()
        self._refresh_environment(require_dependencies=False)

    def _build_widgets(self):
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="auto-rewards",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, padx=24, pady=(24, 18))

        info_frame = ctk.CTkFrame(self)
        info_frame.grid(row=1, column=0, padx=24, sticky="ew")
        info_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(info_frame, text="Browser:").grid(
            row=0, column=0, padx=(16, 8), pady=(12, 6), sticky="w"
        )
        ctk.CTkLabel(info_frame, textvariable=self.browser_var).grid(
            row=0, column=1, padx=(0, 16), pady=(12, 6), sticky="w"
        )
        ctk.CTkLabel(info_frame, text="Session:").grid(
            row=1, column=0, padx=(16, 8), pady=(6, 12), sticky="w"
        )
        ctk.CTkLabel(info_frame, textvariable=self.session_var).grid(
            row=1, column=1, padx=(0, 16), pady=(6, 12), sticky="w"
        )

        fields_frame = ctk.CTkFrame(self, fg_color="transparent")
        fields_frame.grid(row=2, column=0, padx=24, pady=18, sticky="ew")
        fields_frame.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(fields_frame, text="Searches").grid(
            row=0, column=0, padx=(0, 8), sticky="w"
        )
        self.searches_entry = ctk.CTkEntry(
            fields_frame, textvariable=self.searches_var, width=100
        )
        self.searches_entry.grid(row=0, column=1, padx=(0, 18), sticky="ew")

        ctk.CTkLabel(fields_frame, text="Delay").grid(
            row=0, column=2, padx=(0, 8), sticky="w"
        )
        self.delay_entry = ctk.CTkEntry(
            fields_frame, textvariable=self.delay_var, width=100
        )
        self.delay_entry.grid(row=0, column=3, sticky="ew")

        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.grid(row=3, column=0, padx=24, sticky="ew")
        buttons_frame.grid_columnconfigure((0, 1), weight=1)

        self.start_button = ctk.CTkButton(
            buttons_frame, text="Start", command=self.start
        )
        self.start_button.grid(row=0, column=0, padx=(0, 6), sticky="ew")
        self.stop_button = ctk.CTkButton(
            buttons_frame,
            text="Stop",
            command=self.stop,
            state="disabled",
        )
        self.stop_button.grid(row=0, column=1, padx=(6, 0), sticky="ew")

        self.progress = ctk.CTkProgressBar(self)
        self.progress.grid(row=4, column=0, padx=24, pady=(24, 10), sticky="ew")
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(
            self,
            textvariable=self.status_var,
            wraplength=420,
        )
        self.status_label.grid(row=5, column=0, padx=24, pady=(0, 20))

    def _load_initial_values(self):
        try:
            config = core.load_config(core.get_config_path()) or {}
        except ValueError as error:
            config = {}
            self.status_var.set(f"Config error: {error}")

        self.searches_var.set(str(config.get("searches", core.DEFAULT_SEARCH_COUNT)))
        self.delay_var.set(str(config.get("delay", core.DEFAULT_SEARCH_DELAY_SECONDS)))

    def _refresh_environment(self, require_dependencies):
        messages = []
        environment_info = core.check_environment(
            require_dependencies=require_dependencies,
            message_callback=messages.append,
        )

        if environment_info:
            self.browser_var.set(
                core.format_browser_name(environment_info["browser"])
            )
            self.session_var.set(
                core.format_session(
                    environment_info["session"], environment_info["compositor"]
                )
            )

        if messages:
            self.status_var.set(" ".join(messages))

        return environment_info

    def start(self):
        try:
            search_count = core.positive_integer(self.searches_var.get())
            search_delay = core.positive_number(self.delay_var.get())
        except argparse.ArgumentTypeError as error:
            self.status_var.set(f"Invalid value: {error}")
            return

        environment_info = self._refresh_environment(require_dependencies=True)
        if environment_info is None:
            return

        self.search_count = search_count
        self.cancel_event = threading.Event()
        self.progress.set(0)
        self._set_running(True)
        self.status_var.set("Starting searches...")

        self.worker = threading.Thread(
            target=self._run_searches,
            args=(search_count, search_delay),
            daemon=True,
        )
        self.worker.start()

    def stop(self):
        if self.cancel_event is not None:
            self.cancel_event.set()
            self.stop_button.configure(state="disabled")
            self.status_var.set("Stopping safely...")

    def _run_searches(self, search_count, search_delay):
        try:
            completed, cancelled = core.open_tabs(
                search_count,
                search_delay,
                progress_callback=self._queue_progress,
                status_callback=self._queue_status,
                cancel_event=self.cancel_event,
            )
        except OSError as error:
            self.after(0, self._finish_with_error, str(error))
            return

        self.after(0, self._finish, completed, cancelled)

    def _queue_progress(self, completed, total):
        self.after(0, self._update_progress, completed, total)

    def _queue_status(self, message):
        self.after(0, self.status_var.set, message)

    def _update_progress(self, completed, total):
        self.progress.set(completed / total)
        self.status_var.set(f"Completed {completed}/{total} searches")

    def _finish(self, completed, cancelled):
        self._set_running(False)
        if cancelled:
            self.status_var.set(
                f"Cancelled. {completed}/{self.search_count} searches completed."
            )
        else:
            self.progress.set(1)
            self.status_var.set(f"Completed {completed} searches.")

    def _finish_with_error(self, message):
        self._set_running(False)
        self.status_var.set(f"Error: {message}")

    def _set_running(self, running):
        field_state = "disabled" if running else "normal"
        self.searches_entry.configure(state=field_state)
        self.delay_entry.configure(state=field_state)
        self.start_button.configure(state=field_state)
        self.stop_button.configure(state="normal" if running else "disabled")


def main():
    app = AutoRewardsApp()
    app.mainloop()


if __name__ == "__main__":
    main()
