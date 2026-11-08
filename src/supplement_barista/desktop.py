"""Desktop application for the Supplement Barista scheduling foundation."""

from __future__ import annotations

import sqlite3
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from supplement_barista import __version__
from supplement_barista.core import SupplementStore
from supplement_barista.csv_io import export_schedule, import_schedule
from supplement_barista.library import search_supplements


def default_database_path() -> Path:
    location = Path.home() / "SupplementBarista"
    location.mkdir(parents=True, exist_ok=True)
    return location / "supplements.sqlite3"


class SupplementBaristaApp:
    def __init__(self, root: tk.Tk, store: SupplementStore) -> None:
        self.root = root
        self.store = store
        self.root.title(f"Supplement Barista v2 — Rev {__version__}")
        self.root.geometry("1050x650")
        self.profile_ids: dict[str, int] = {}
        self.supplement_ids: dict[str, int] = {}
        self.profile_var = tk.StringVar()
        self.supplement_var = tk.StringVar()
        self.time_var = tk.StringVar(value="08:00")
        self.quantity_var = tk.StringVar(value="1")
        self.unit_var = tk.StringVar(value="capsule")
        self.save_status = tk.StringVar(value="Changes save automatically")
        self._build()
        self.refresh_catalog()
        self.refresh_profiles()

    def _build(self) -> None:
        frame = ttk.Frame(self.root, padding=14)
        frame.pack(fill="both", expand=True)
        profile = ttk.LabelFrame(frame, text="Profile", padding=10)
        profile.pack(fill="x")
        ttk.Label(profile, text="Active profile").pack(side="left")
        self.profile_box = ttk.Combobox(
            profile, textvariable=self.profile_var, state="readonly", width=30
        )
        self.profile_box.pack(side="left", padx=8)
        self.profile_box.bind("<<ComboboxSelected>>", lambda _event: self.refresh_schedule())
        ttk.Button(profile, text="New profile", command=self.new_profile).pack(side="left")
        ttk.Button(profile, text="Rename", command=self.rename_profile).pack(side="left")
        ttk.Button(profile, text="Delete", command=self.delete_profile).pack(side="left")

        catalog = ttk.LabelFrame(frame, text="Supplement catalog", padding=10)
        catalog.pack(fill="x", pady=10)
        ttk.Label(catalog, text="Supplement").pack(side="left")
        self.supplement_box = ttk.Combobox(
            catalog, textvariable=self.supplement_var, state="readonly", width=35
        )
        self.supplement_box.pack(side="left", padx=8)
        ttk.Button(catalog, text="Browse library...", command=self.browse_library).pack(side="left")
        ttk.Button(catalog, text="Add custom...", command=self.new_supplement).pack(side="left")
        ttk.Button(catalog, text="Edit", command=self.edit_supplement).pack(side="left")
        ttk.Button(catalog, text="Delete", command=self.delete_supplement).pack(side="left")

        dose = ttk.LabelFrame(frame, text="Daily dose", padding=10)
        dose.pack(fill="x")
        ttk.Label(dose, text="Time").pack(side="left")
        self.time_box = ttk.Combobox(
            dose,
            textvariable=self.time_var,
            values=[f"{hour:02d}:{minute:02d}" for hour in range(24) for minute in (0, 30)],
            state="readonly",
            width=8,
        )
        self.time_box.pack(side="left", padx=5)
        ttk.Label(dose, text="Quantity").pack(side="left")
        ttk.Entry(dose, textvariable=self.quantity_var, width=8).pack(side="left", padx=5)
        ttk.Label(dose, text="Unit").pack(side="left")
        ttk.Entry(dose, textvariable=self.unit_var, width=15).pack(side="left", padx=5)
        ttk.Button(dose, text="Add dose", command=self.add_dose).pack(side="left", padx=4)
        ttk.Button(dose, text="Update selected", command=self.update_dose).pack(side="left")
        ttk.Button(dose, text="Delete selected", command=self.delete_dose).pack(side="left")

        schedule = ttk.LabelFrame(frame, text="Daily schedule", padding=10)
        schedule.pack(fill="both", expand=True, pady=10)
        columns = ("time", "supplement", "form", "quantity", "unit")
        self.table = ttk.Treeview(schedule, columns=columns, show="headings", selectmode="browse")
        for column in columns:
            self.table.heading(column, text=column.title())
            self.table.column(column, width=130 if column != "supplement" else 320)
        self.table.tag_configure("empty", foreground="#888888")
        self.table.pack(side="left", fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.select_dose)
        scrollbar = ttk.Scrollbar(schedule, orient="vertical", command=self.table.yview)
        scrollbar.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=scrollbar.set)
        actions = ttk.Frame(frame)
        actions.pack(fill="x")
        ttk.Button(actions, text="Import schedule CSV", command=self.import_csv).pack(side="left")
        ttk.Button(actions, text="Export schedule CSV", command=self.export_csv).pack(side="left")
        ttk.Button(actions, text="Restore Backup...", command=self.restore).pack(side="right")
        ttk.Button(actions, text="Save Backup...", command=self.backup).pack(side="right")
        ttk.Label(frame, textvariable=self.save_status).pack(anchor="w", pady=(6, 0))

    def _execute(self, action) -> None:
        try:
            action()
        except (ValueError, LookupError, sqlite3.Error, OSError) as exc:
            messagebox.showerror("Supplement Barista", str(exc), parent=self.root)

    def _profile_id(self) -> int:
        if self.profile_var.get() not in self.profile_ids:
            raise ValueError("Select or create a profile first")
        return self.profile_ids[self.profile_var.get()]

    def _supplement_id(self) -> int:
        if self.supplement_var.get() not in self.supplement_ids:
            raise ValueError("Select or create a supplement first")
        return self.supplement_ids[self.supplement_var.get()]

    def _selected_dose_id(self) -> int:
        selection = self.table.selection()
        if not selection:
            raise ValueError("Select a schedule row first")
        if selection[0].startswith("slot:"):
            raise ValueError("Select a scheduled dose, not an empty time slot")
        return int(selection[0])

    def refresh_profiles(self) -> None:
        previous = self.profile_var.get()
        self.profile_ids = {row["name"]: row["id"] for row in self.store.profiles()}
        self.profile_box["values"] = list(self.profile_ids)
        self.profile_var.set(
            previous if previous in self.profile_ids else next(iter(self.profile_ids), "")
        )
        self.refresh_schedule()

    def refresh_catalog(self) -> None:
        previous = self.supplement_var.get()
        self.supplement_ids = {
            row["name"]: row["id"] for row in self.store.supplements()
        }
        self.supplement_box["values"] = list(self.supplement_ids)
        self.supplement_var.set(
            previous if previous in self.supplement_ids else next(iter(self.supplement_ids), "")
        )

    def refresh_schedule(self) -> None:
        for item in self.table.get_children():
            self.table.delete(item)
        if self.profile_var.get() not in self.profile_ids:
            return
        schedule = self.store.schedule(self._profile_id())
        by_time = {}
        for row in schedule:
            by_time.setdefault(row["time"], []).append(row)
        for hour in range(24):
            for minute in (0, 30):
                slot = f"{hour:02d}:{minute:02d}"
                rows = by_time.get(slot, [])
                if not rows:
                    self.table.insert(
                        "", "end", iid=f"slot:{slot}",
                        values=(slot, "—", "", "", ""), tags=("empty",),
                    )
                for row in rows:
                    self.table.insert(
                        "", "end", iid=str(row["id"]),
                        values=(
                            row["time"], row["supplement"], row["form"],
                            row["quantity"], row["unit"],
                        ),
                    )

    def new_profile(self) -> None:
        name = simpledialog.askstring("New profile", "Profile name:", parent=self.root)
        if name is not None:
            self._execute(lambda: self._create_profile(name))

    def _create_profile(self, name: str) -> None:
        self.store.add_profile(name)
        self.refresh_profiles()
        self.profile_var.set(name.strip())
        self.refresh_schedule()
        self._saved()

    def rename_profile(self) -> None:
        def action() -> None:
            profile_id = self._profile_id()
            name = simpledialog.askstring(
                "Rename profile", "New name:", initialvalue=self.profile_var.get(),
                parent=self.root,
            )
            if name is not None:
                self.store.rename_profile(profile_id, name)
                self.refresh_profiles()
                self.profile_var.set(name.strip())
                self.refresh_schedule()
                self._saved()
        self._execute(action)

    def delete_profile(self) -> None:
        def action() -> None:
            profile_id = self._profile_id()
            if messagebox.askyesno(
                "Delete profile", "Delete this profile and all its scheduled doses?",
                parent=self.root,
            ):
                self.store.delete_profile(profile_id)
                self.refresh_profiles()
                self._saved()
        self._execute(action)

    def _supplement_dialog(self, title: str, current: dict | None = None) -> None:
        name = simpledialog.askstring(
            title, "Supplement name:",
            initialvalue=current["name"] if current else "", parent=self.root,
        )
        if name is None:
            return
        form = simpledialog.askstring(
            title, "Form (capsule, powder, liquid, etc.):",
            initialvalue=current["form"] if current else "Capsule", parent=self.root,
        )
        if form is None:
            return
        notes = simpledialog.askstring(
            title, "Personal notes:",
            initialvalue=current["notes"] if current else "", parent=self.root,
        )
        if notes is None:
            return
        if current:
            self.store.update_supplement(current["id"], name, form, notes)
        else:
            self.store.add_supplement(name, form, notes)
        self.refresh_catalog()
        self.supplement_var.set(name.strip())
        self.refresh_schedule()
        self._saved()

    def browse_library(self) -> None:
        window = tk.Toplevel(self.root)
        window.title("Supplement library — select or add custom")
        window.geometry("590x650")
        window.transient(self.root)
        window.grab_set()
        panel = ttk.Frame(window, padding=12)
        panel.pack(fill="both", expand=True)
        ttk.Label(
            panel,
            text="Build your daily schedule — add multiple supplements without closing this window.",
        ).pack(anchor="w")
        search = tk.StringVar()
        ttk.Label(panel, text="STEP 1 — Find and select a supplement").pack(
            anchor="w", pady=(12, 0)
        )
        entry = ttk.Entry(panel, textvariable=search)
        entry.pack(fill="x")
        listbox = tk.Listbox(panel, height=17, exportselection=False)
        listbox.pack(fill="both", expand=True, pady=10)
        dose_fields = ttk.LabelFrame(panel, text="STEP 2 — Enter quantity, unit and time", padding=8)
        dose_fields.pack(fill="x", pady=(0, 10))
        ttk.Label(dose_fields, text="Time").grid(row=0, column=0, sticky="w")
        time_choice = tk.StringVar(value=self.time_var.get())
        ttk.Combobox(
            dose_fields, textvariable=time_choice, state="readonly", width=8,
            values=[f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)],
        ).grid(row=1, column=0, padx=(0, 12))
        ttk.Label(dose_fields, text="Quantity").grid(row=0, column=1, sticky="w")
        amount_choice = tk.StringVar(value="")
        amount_entry = ttk.Entry(dose_fields, textvariable=amount_choice, width=12)
        amount_entry.grid(row=1, column=1, padx=(0, 12))
        ttk.Label(dose_fields, text="Unit (mg, g, capsule)").grid(
            row=0, column=2, sticky="w"
        )
        unit_choice = tk.StringVar(value="")
        ttk.Entry(dose_fields, textvariable=unit_choice, width=18).grid(row=1, column=2)
        status = tk.StringVar(value="Select a supplement, then enter its dose and time.")
        entries: list[tuple[str, str]] = []

        def refresh(*_args) -> None:
            entries[:] = search_supplements(search.get())
            listbox.delete(0, "end")
            for name, form in entries:
                listbox.insert("end", f"{name}  ({form})")

        def add_selected() -> None:
            selection = listbox.curselection()
            if not selection:
                messagebox.showinfo(
                    "Choose a supplement", "Select an item from the list.", parent=window
                )
                return
            name, form = entries[selection[0]]
            try:
                profile_id = self._profile_id()
                quantity = float(amount_choice.get())
                unit = unit_choice.get().strip()
                import math
                if not math.isfinite(quantity) or quantity <= 0 or not unit:
                    raise ValueError("Enter a positive quantity and a unit")
                time = time_choice.get()
                if time not in [
                    f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)
                ]:
                    raise ValueError("Select a valid 30-minute time slot")
                existing = next(
                    (item for item in self.store.supplements()
                     if item["name"].casefold() == name.casefold()),
                    None,
                )
                supplement_id = (
                    existing["id"] if existing
                    else self.store.add_supplement(name, form)
                )
                self.store.add_dose(profile_id, supplement_id, time, quantity, unit)
            except (ValueError, LookupError, sqlite3.Error) as exc:
                messagebox.showerror("Supplement Barista", str(exc), parent=window)
                return
            self.refresh_catalog()
            self.supplement_var.set(name if not existing else existing["name"])
            self.time_var.set(time)
            self.quantity_var.set(str(quantity))
            self.unit_var.set(unit)
            self.refresh_schedule()
            self._saved()
            status.set(f"Added: {name} — {quantity:g} {unit} at {time}. Add another or close.")
            amount_choice.set("")
            unit_choice.set("")
            listbox.selection_clear(0, "end")
            entry.focus_set()

        search.trace_add("write", refresh)
        refresh()
        listbox.bind("<Double-Button-1>", lambda _event: amount_entry.focus_set())
        buttons = ttk.Frame(panel)
        buttons.pack(fill="x")
        ttk.Button(
            buttons, text="STEP 3 — Add to schedule", command=add_selected
        ).pack(side="left")
        ttk.Button(
            buttons, text="Add custom...", command=lambda: (window.destroy(), self.new_supplement())
        ).pack(side="left", padx=8)
        ttk.Button(buttons, text="Done / Close", command=window.destroy).pack(side="right")
        ttk.Label(panel, textvariable=status, wraplength=540).pack(anchor="w", pady=(10, 0))
        entry.focus_set()

    def new_supplement(self) -> None:
        self._execute(lambda: self._supplement_dialog("Add supplement"))

    def edit_supplement(self) -> None:
        def action() -> None:
            selected_id = self._supplement_id()
            current = next(
                row for row in self.store.supplements() if row["id"] == selected_id
            )
            self._supplement_dialog("Edit supplement", current)
        self._execute(action)

    def delete_supplement(self) -> None:
        def action() -> None:
            supplement_id = self._supplement_id()
            if messagebox.askyesno(
                "Delete supplement", "Delete supplement and all scheduled doses?",
                parent=self.root,
            ):
                self.store.delete_supplement(supplement_id)
                self.refresh_catalog()
                self.refresh_schedule()
                self._saved()
        self._execute(action)

    def _dose_values(self) -> tuple[str, float, str]:
        return self.time_var.get(), float(self.quantity_var.get()), self.unit_var.get()

    def add_dose(self) -> None:
        def action() -> None:
            time, quantity, unit = self._dose_values()
            self.store.add_dose(
                self._profile_id(), self._supplement_id(), time, quantity, unit
            )
            self.refresh_schedule()
            self._saved()
        self._execute(action)

    def update_dose(self) -> None:
        def action() -> None:
            dose_id = self._selected_dose_id()
            time, quantity, unit = self._dose_values()
            self.store.update_dose(dose_id, time, quantity, unit)
            self.refresh_schedule()
            self._saved()
        self._execute(action)

    def delete_dose(self) -> None:
        def action() -> None:
            dose_id = self._selected_dose_id()
            if messagebox.askyesno(
                "Delete dose", "Delete this scheduled dose?", parent=self.root
            ):
                self.store.delete_dose(dose_id)
                self.refresh_schedule()
                self._saved()
        self._execute(action)

    def select_dose(self, _event) -> None:
        selection = self.table.selection()
        if selection:
            values = self.table.item(selection[0], "values")
            self.time_var.set(values[0])
            if selection[0].startswith("slot:"):
                return
            self.supplement_var.set(values[1])
            self.quantity_var.set(str(values[3]))
            self.unit_var.set(values[4])

    def import_csv(self) -> None:
        def action() -> None:
            profile_id = self._profile_id()
            path = filedialog.askopenfilename(
                parent=self.root, title="Import schedule CSV",
                filetypes=[("CSV files", "*.csv")],
            )
            if not path:
                return
            if not messagebox.askyesno(
                "Import schedule",
                "Import adds doses to this profile; importing twice creates duplicates. Continue?",
                parent=self.root,
            ):
                return
            count = import_schedule(self.store, profile_id, path)
            self.refresh_catalog()
            self.refresh_schedule()
            self._saved()
            messagebox.showinfo("Import complete", f"Imported {count} doses.", parent=self.root)
        self._execute(action)

    def export_csv(self) -> None:
        def action() -> None:
            profile_id = self._profile_id()
            path = filedialog.asksaveasfilename(
                parent=self.root, title="Export schedule CSV",
                defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
            )
            if not path:
                return
            count = export_schedule(self.store, profile_id, path)
            messagebox.showinfo("Export complete", f"Exported {count} doses.", parent=self.root)
        self._execute(action)

    def _saved(self) -> None:
        self.save_status.set("All changes saved automatically")

    def restore(self) -> None:
        def action() -> None:
            source = filedialog.askopenfilename(
                parent=self.root, title="Choose Supplement Barista backup",
                filetypes=[("SQLite database", "*.sqlite3")],
            )
            if not source:
                return
            if not messagebox.askyesno(
                "Confirm restore",
                "Restore will replace ALL current profiles, supplements, and doses. "
                "You must first save a recovery copy of your current database. Continue?",
                parent=self.root,
            ):
                return
            recovery = filedialog.asksaveasfilename(
                parent=self.root, title="Save current database before restore",
                defaultextension=".sqlite3",
                filetypes=[("SQLite database", "*.sqlite3")],
            )
            if not recovery:
                return
            self.store.restore(source, recovery)
            self.refresh_catalog()
            self.refresh_profiles()
            self._saved()
            messagebox.showinfo(
                "Restore complete",
                "Backup restored. A recovery copy of your previous database was saved.",
                parent=self.root,
            )
        self._execute(action)

    def backup(self) -> None:
        path = filedialog.asksaveasfilename(
            parent=self.root, title="Save backup", defaultextension=".sqlite3",
            filetypes=[("SQLite database", "*.sqlite3")],
        )
        if path:
            self._execute(lambda: self._save_backup(path))

    def _save_backup(self, path: str) -> None:
        overwrite = Path(path).exists()
        if overwrite and not messagebox.askyesno(
            "Replace existing backup?",
            "This will replace the selected backup with the current database. "
            "The previous backup will no longer be available. Continue?",
            parent=self.root,
        ):
            return
        self.store.backup(path, overwrite=overwrite)
        messagebox.showinfo("Backup", "Database backup saved.", parent=self.root)


def main() -> None:
    root = tk.Tk()
    store = SupplementStore(default_database_path())
    SupplementBaristaApp(root, store)
    try:
        root.mainloop()
    finally:
        store.close()


if __name__ == "__main__":
    main()
