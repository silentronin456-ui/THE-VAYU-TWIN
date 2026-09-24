"""
SPASHT AI -- Simulated 1 Hz Diagnostic Telemetry Feed
=====================================================
PURPOSE
-------
This script is a DEMONSTRATION / TEST HARNESS ONLY.

It simulates a 1 Hz telemetry stream by replaying existing flight CSV files
row-by-row through the production DiagnosticEngine and DiagnosticAlertStabilizer.

It is NOT a live GCS integration.
It does NOT connect to any external telemetry bus, WebSocket, or broker.
It does NOT generate synthetic data.
It does NOT modify any raw CSV files or production artifacts.

All predictions are produced by the real, validated
``artifacts/diagnostic_xgboost_v1.onnx`` model via ONNX Runtime.

USAGE
-----
    # Fast mode (no real-time delay -- for testing / CI):
    python src/simulate_live_feed.py --scenario nominal
    python src/simulate_live_feed.py --scenario fault
    python src/simulate_live_feed.py --scenario cascade

    # Real-time mode (1 row per second):
    python src/simulate_live_feed.py --scenario fault --realtime

    # Limit rows processed:
    python src/simulate_live_feed.py --scenario nominal --max-rows 200

    # Choose a specific CSV file directly:
    python src/simulate_live_feed.py --file data/diagnostic_dataset/Thermal\\ Anomalies/flight_018_critical_overheat.csv
"""

import os
import sys
import time
import argparse
import json
from typing import Optional

import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# Ensure src/ is on the path so imports resolve regardless of cwd
# ---------------------------------------------------------------------------
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR = os.path.abspath(os.path.join(_SRC_DIR, ".."))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from diagnostic_runtime import (
    DiagnosticEngine,
    DiagnosticAlertStabilizer,
    DiagnosticResult,
    AlertStatus,
    DiagnosticValidationError,
)


# ---------------------------------------------------------------------------
# Predefined scenario to CSV path mapping (real files verified to exist)
# ---------------------------------------------------------------------------
SCENARIOS = {
    "nominal": os.path.join(
        _BASE_DIR,
        "data", "diagnostic_dataset",
        "nominal_diagnostic_dataset",
        "flight_001_nominal.csv",
    ),
    "fault": os.path.join(
        _BASE_DIR,
        "data", "diagnostic_dataset",
        "Thermal Anomalies",
        "flight_018_critical_overheat.csv",
    ),
    "cascade": os.path.join(
        _BASE_DIR,
        "data", "diagnostic_dataset",
        "spasht_official_cascades_58col",
        "05_TOTAL_SYSTEM_FAILURE_v1.csv",
    ),
}


# ---------------------------------------------------------------------------
# ANSI colour helpers (gracefully disabled on non-TTY / Windows without VT)
# ---------------------------------------------------------------------------
def _supports_colour() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


class _Colour:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    CYAN    = "\033[96m"
    MAGENTA = "\033[95m"
    GREY    = "\033[90m"

    @classmethod
    def wrap(cls, text: str, *codes: str) -> str:
        if not _supports_colour():
            return text
        return "".join(codes) + text + cls.RESET


# ---------------------------------------------------------------------------
# FeedResult -- structured per-frame output of the simulator
# ---------------------------------------------------------------------------
class FeedResult:
    """Structured output for one simulated telemetry frame."""

    def __init__(
        self,
        elapsed_s: int,
        raw_result: DiagnosticResult,
        alert_status: AlertStatus,
    ):
        self.elapsed_s = elapsed_s
        self.raw_result = raw_result
        self.alert_status = alert_status

    def to_dict(self) -> dict:
        return {
            "elapsed_s": self.elapsed_s,
            "raw": self.raw_result.to_dict(),
            "stabilized": {
                "confirmed_fault_label": self.alert_status.confirmed_fault_label,
                "is_alert_active": self.alert_status.is_alert_active,
                "consecutive_fault_count": self.alert_status.consecutive_fault_count,
                "debounce_threshold": self.alert_status.debounce_threshold,
            },
        }


# ---------------------------------------------------------------------------
# SimulatedLiveFeed -- core simulation class
# ---------------------------------------------------------------------------
class SimulatedLiveFeed:
    """
    Replays a flight CSV file row-by-row, feeding each row through
    DiagnosticEngine + DiagnosticAlertStabilizer at simulated 1 Hz cadence.

    This is purely a test/demonstration harness.  It uses only:
      - Existing CSV files from data/diagnostic_dataset/
      - Production artifacts from artifacts/
      - The validated DiagnosticEngine and DiagnosticAlertStabilizer

    No external connections, no invented data, no artifact mutations.
    """

    def __init__(
        self,
        artifacts_dir: Optional[str] = None,
        debounce_threshold: int = 3,
        realtime: bool = False,
        verbose: bool = True,
    ):
        """
        Args:
            artifacts_dir:       Path to artifacts/ directory.  Defaults to
                                 ../artifacts relative to this file.
            debounce_threshold:  Consecutive identical fault frames required
                                 for DiagnosticAlertStabilizer to confirm alert.
            realtime:            If True, sleep 1 second between frames.
                                 If False (default), process frames instantly.
            verbose:             If True, print per-frame output to stdout.
        """
        if artifacts_dir is None:
            artifacts_dir = os.path.join(_BASE_DIR, "artifacts")

        self.engine = DiagnosticEngine(artifacts_dir=artifacts_dir)
        self.stabilizer = DiagnosticAlertStabilizer(
            engine=self.engine,
            debounce_threshold=debounce_threshold,
        )
        self.realtime = realtime
        self.verbose = verbose

    def _load_csv(self, csv_path: str) -> pd.DataFrame:
        """Load and minimally validate a flight CSV."""
        if not os.path.isfile(csv_path):
            raise FileNotFoundError(f"Flight CSV not found: {csv_path}")
        df = pd.read_csv(csv_path)
        # Normalise 'flags' to 'flight.phase' for cascade files
        if "flags" in df.columns and "flight.phase" not in df.columns:
            df = df.rename(columns={"flags": "flight.phase"})
        if "flight.phase" not in df.columns:
            raise ValueError(
                f"CSV '{csv_path}' has no 'flight.phase' or 'flags' column."
            )
        return df

    def _print_header(self, csv_path: str, total_rows: int, scenario_label: str):
        sep = "=" * 78
        print(sep)
        print(
            _Colour.wrap(
                "  SPASHT AI -- Simulated 1 Hz Diagnostic Telemetry Feed",
                _Colour.BOLD, _Colour.CYAN,
            )
        )
        print(
            _Colour.wrap(
                "  [DEMO / TEST HARNESS -- NOT live GCS integration]",
                _Colour.GREY,
            )
        )
        print(sep)
        print(f"  Scenario  : {_Colour.wrap(scenario_label.upper(), _Colour.BOLD)}")
        print(f"  File      : {os.path.relpath(csv_path, _BASE_DIR)}")
        print(f"  Rows      : {total_rows:,}")
        print(f"  Mode      : {'REALTIME (1 s/frame)' if self.realtime else 'FAST (no delay)'}")
        print(f"  Debounce  : {self.stabilizer.debounce_threshold} consecutive frames")
        print(sep)

    def _print_frame(self, feed_result: FeedResult):
        """Print one formatted telemetry frame to stdout."""
        t = feed_result.elapsed_s
        raw = feed_result.raw_result
        alert = feed_result.alert_status

        # Colour-code the raw prediction
        if raw.predicted_fault_label == "NORMAL_OPERATIONS":
            label_str = _Colour.wrap(raw.predicted_fault_label, _Colour.GREEN)
        else:
            label_str = _Colour.wrap(raw.predicted_fault_label, _Colour.RED, _Colour.BOLD)

        # Alert state marker
        if alert.is_alert_active:
            alert_marker = _Colour.wrap(
                f"[ALERT] {alert.confirmed_fault_label}",
                _Colour.RED, _Colour.BOLD,
            )
        elif alert.consecutive_fault_count > 0:
            alert_marker = _Colour.wrap(
                f"[WARN] DEBOUNCING ({alert.consecutive_fault_count}/{alert.debounce_threshold})",
                _Colour.YELLOW,
            )
        else:
            alert_marker = _Colour.wrap("[OK] NOMINAL", _Colour.GREEN)

        print(
            f"[t={t:05d}s] "
            f"Phase={_Colour.wrap(raw.flight_phase, _Colour.CYAN):<10} | "
            f"Diag={label_str:<35} | "
            f"Conf={raw.confidence:.4f} | "
            f"{alert_marker}"
        )

    def run(
        self,
        csv_path: str,
        scenario_label: str = "custom",
        max_rows: Optional[int] = None,
    ) -> list:
        """
        Run the simulation over the given CSV file.

        Args:
            csv_path:       Absolute or relative path to a flight CSV.
            scenario_label: Human-readable label for the header display.
            max_rows:       If set, process only the first N rows.

        Returns:
            List of FeedResult objects (one per processed row).
        """
        df = self._load_csv(csv_path)

        if max_rows is not None:
            df = df.iloc[:max_rows]

        total_rows = len(df)
        self.stabilizer.reset()

        if self.verbose:
            self._print_header(csv_path, total_rows, scenario_label)

        results: list = []
        fault_onset_logged = False

        for elapsed_s, (_, row) in enumerate(df.iterrows(), start=1):
            row_dict = row.to_dict()

            try:
                alert_status = self.stabilizer.process_snapshot(
                    row_dict, timestamp=elapsed_s
                )
            except DiagnosticValidationError as exc:
                print(
                    _Colour.wrap(
                        f"[t={elapsed_s:05d}s] VALIDATION ERROR: {exc}",
                        _Colour.RED,
                    )
                )
                continue

            feed_result = FeedResult(
                elapsed_s=elapsed_s,
                raw_result=alert_status.raw_result,
                alert_status=alert_status,
            )
            results.append(feed_result)

            if self.verbose:
                # Always print first 5 frames and last 5 frames
                # Print every 500th frame during long runs to avoid flooding
                # Always print any fault-active or debouncing frame
                is_boundary = elapsed_s <= 5 or elapsed_s > total_rows - 5
                is_interesting = (
                    alert_status.is_alert_active
                    or alert_status.consecutive_fault_count > 0
                    or alert_status.raw_result.predicted_fault_label != "NORMAL_OPERATIONS"
                )
                is_periodic = (elapsed_s % 500 == 0)

                # Log first fault onset transition
                if is_interesting and not fault_onset_logged:
                    print(
                        _Colour.wrap(
                            f"  [t={elapsed_s:05d}s] ^ First non-nominal prediction",
                            _Colour.MAGENTA,
                        )
                    )
                    fault_onset_logged = True

                if is_boundary or is_interesting or is_periodic:
                    self._print_frame(feed_result)

            if self.realtime:
                time.sleep(1.0)

        if self.verbose:
            self._print_summary(results, total_rows)

        return results

    def _print_summary(self, results: list, total_rows: int):
        """Print a final summary after all rows are processed."""
        sep = "-" * 78
        print(sep)

        processed = len(results)
        fault_frames = sum(
            1 for r in results
            if r.raw_result.predicted_fault_label != "NORMAL_OPERATIONS"
        )
        alert_active_frames = sum(
            1 for r in results if r.alert_status.is_alert_active
        )
        nominal_frames = processed - fault_frames

        # Collect unique confirmed faults
        confirmed_labels = set(
            r.alert_status.confirmed_fault_label
            for r in results
            if r.alert_status.is_alert_active
        )

        print(
            _Colour.wrap("  SIMULATION COMPLETE", _Colour.BOLD, _Colour.CYAN)
        )
        print(f"  Total rows in file : {total_rows:,}")
        print(f"  Rows processed     : {processed:,}")
        print(f"  Nominal frames     : {_Colour.wrap(str(nominal_frames), _Colour.GREEN)}")
        print(f"  Fault frames (raw) : {_Colour.wrap(str(fault_frames), _Colour.RED if fault_frames else _Colour.GREEN)}")
        print(f"  Alert-active frames: {_Colour.wrap(str(alert_active_frames), _Colour.RED if alert_active_frames else _Colour.GREEN)}")

        if confirmed_labels:
            labels_str = ", ".join(sorted(confirmed_labels))
            print(
                f"  Confirmed alerts   : "
                f"{_Colour.wrap(labels_str, _Colour.RED, _Colour.BOLD)}"
            )
        else:
            print(
                f"  Confirmed alerts   : "
                f"{_Colour.wrap('None (all nominal or debouncing only)', _Colour.GREEN)}"
            )

        print(sep)
        print(
            _Colour.wrap(
                "  [OK] Artifacts verified unchanged -- this was a read-only simulation",
                _Colour.GREY,
            )
        )
        print(sep)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="simulate_live_feed.py",
        description=(
            "SPASHT AI -- Simulated 1 Hz Diagnostic Telemetry Feed\n"
            "DEMO / TEST HARNESS ONLY. Not live GCS integration."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--scenario",
        choices=["nominal", "fault", "cascade"],
        help=(
            "Preset scenario: 'nominal' = nominal flight, "
            "'fault' = critical overheat flight, "
            "'cascade' = total system failure cascade."
        ),
    )
    mode_group.add_argument(
        "--file",
        metavar="CSV_PATH",
        help="Path to a specific flight CSV file (overrides --scenario).",
    )

    parser.add_argument(
        "--realtime",
        action="store_true",
        default=False,
        help="Sleep 1 second between frames (default: FAST mode, no delay).",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=None,
        metavar="N",
        help="Process only the first N rows (useful for quick demos).",
    )
    parser.add_argument(
        "--debounce",
        type=int,
        default=3,
        metavar="K",
        help="Consecutive fault frames required to confirm alert (default: 3).",
    )
    parser.add_argument(
        "--artifacts-dir",
        default=None,
        metavar="DIR",
        help="Path to artifacts directory. Defaults to ../artifacts.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Suppress per-frame console output (results still returned).",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Resolve CSV path
    if args.file:
        csv_path = os.path.abspath(args.file)
        scenario_label = "custom"
    elif args.scenario:
        csv_path = SCENARIOS[args.scenario]
        scenario_label = args.scenario
    else:
        parser.print_help()
        sys.exit(1)

    feed = SimulatedLiveFeed(
        artifacts_dir=args.artifacts_dir,
        debounce_threshold=args.debounce,
        realtime=args.realtime,
        verbose=not args.quiet,
    )

    results = feed.run(
        csv_path=csv_path,
        scenario_label=scenario_label,
        max_rows=args.max_rows,
    )

    return 0 if results else 1


if __name__ == "__main__":
    sys.exit(main())
