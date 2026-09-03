import argparse
import threading

import customtkinter as ctk

import main as core


class AutoRewardsApp(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        super().__init__()
        self.title("auto-rewards")
        self.geometry("580x600")
        self.minsize(520, 560)
        self.configure(fg_color="#0f1115")

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
        self.grid_rowconfigure(3, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=32, pady=(28, 20), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="auto-rewards",
            font=ctk.CTkFont(size=28, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            header,
            text="Automate reward searches on Linux / Wayland",
            text_color="#9ca3af",
            anchor="w",
        ).grid(row=1, column=0, pady=(4, 0), sticky="ew")

        info_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="#191c22")
        info_frame.grid(row=1, column=0, padx=32, pady=(0, 14), sticky="ew")
        info_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            info_frame,
            text="ENVIRONMENT",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#9ca3af",
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(16, 12), sticky="w")
        ctk.CTkLabel(info_frame, text="Browser", text_color="#9ca3af").grid(
            row=1, column=0, padx=(20, 20), pady=(0, 8), sticky="w"
        )
        ctk.CTkLabel(
            info_frame,
            textvariable=self.browser_var,
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=1, column=1, padx=(0, 20), pady=(0, 8), sticky="e")
        ctk.CTkLabel(info_frame, text="Session", text_color="#9ca3af").grid(
            row=2, column=0, padx=(20, 20), pady=(0, 16), sticky="w"
        )
        ctk.CTkLabel(
            info_frame,
            textvariable=self.session_var,
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=2, column=1, padx=(0, 20), pady=(0, 16), sticky="e")

        fields_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="#191c22")
        fields_frame.grid(row=2, column=0, padx=32, pady=(0, 14), sticky="ew")
        fields_frame.grid_columnconfigure((0, 1), weight=1, uniform="fields")

        ctk.CTkLabel(
            fields_frame,
            text="CONFIGURATION",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#9ca3af",
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(16, 12), sticky="w")

        searches_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        searches_frame.grid(row=1, column=0, padx=(20, 8), pady=(0, 18), sticky="ew")
        searches_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(searches_frame, text="Searches", anchor="w").grid(
            row=0, column=0, pady=(0, 6), sticky="ew"
        )
        self.searches_entry = ctk.CTkEntry(
            searches_frame,
            textvariable=self.searches_var,
            height=38,
            border_width=1,
        )
        self.searches_entry.grid(row=1, column=0, sticky="ew")

        delay_frame = ctk.CTkFrame(fields_frame, fg_color="transparent")
        delay_frame.grid(row=1, column=1, padx=(8, 20), pady=(0, 18), sticky="ew")
        delay_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(delay_frame, text="Delay (seconds)", anchor="w").grid(
            row=0, column=0, pady=(0, 6), sticky="ew"
        )
        self.delay_entry = ctk.CTkEntry(
            delay_frame,
            textvariable=self.delay_var,
            height=38,
            border_width=1,
        )
        self.delay_entry.grid(row=1, column=0, sticky="ew")

        execution_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="#191c22")
        execution_frame.grid(
            row=3, column=0, padx=32, pady=(0, 28), sticky="nsew"
        )
        execution_frame.grid_columnconfigure((0, 1), weight=1, uniform="actions")
        execution_frame.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            execution_frame,
            text="EXECUTION",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#9ca3af",
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(16, 14), sticky="w")

        self.start_button = ctk.CTkButton(
            execution_frame,
            text="Start",
            command=self.start,
            height=40,
            font=ctk.CTkFont(weight="bold"),
        )
        self.start_button.grid(
            row=1, column=0, padx=(20, 6), pady=(0, 20), sticky="ew"
        )
        self.stop_button = ctk.CTkButton(
            execution_frame,
            text="Stop",
            command=self.stop,
            state="disabled",
            height=40,
            font=ctk.CTkFont(weight="bold"),
            fg_color="#b91c1c",
            hover_color="#991b1b",
        )
        self.stop_button.grid(
            row=1, column=1, padx=(6, 20), pady=(0, 20), sticky="ew"
        )

        self.progress = ctk.CTkProgressBar(
            execution_frame,
            height=10,
            corner_radius=5,
            progress_color="#3b82f6",
        )
        self.progress.grid(
            row=2, column=0, columnspan=2, padx=20, pady=(0, 16), sticky="ew"
        )
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(
            execution_frame,
            textvariable=self.status_var,
            text_color="#cbd5e1",
            anchor="w",
            justify="left",
            wraplength=480,
        )
        self.status_label.grid(
            row=3,
            column=0,
            columnspan=2,
            padx=20,
            pady=(0, 18),
            sticky="ew",
        )

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
