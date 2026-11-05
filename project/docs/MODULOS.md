# Módulos, classes, funções e dependências

Inventário gerado da árvore final de fontes, sem executar os módulos. Nomes e linhas estão em `INVENTARIO.json`.

## api/api.py

Imports: PIL, io, os, requests


## debug_view.py

Imports: atexit, ctypes, cv2, json, math, multiprocessing, numpy, os, struct, subprocess, sys, time, tkinter, utils

- `_running_as_compiled_executable` (function, linha 20)
- `_get_screen_size` (function, linha 24)
- `DebugViewPublisher` (class, linha 57)
- `DebugViewPublisher.__init__` (function, linha 58)
- `DebugViewPublisher.from_config` (function, linha 88)
- `DebugViewPublisher.publish` (function, linha 100)
- `DebugViewPublisher.publish_debug_data` (function, linha 119)
- `DebugViewPublisher.start_viewer` (function, linha 139)
- `DebugViewPublisher.close` (function, linha 193)
- `read_debug_data` (function, linha 231)
- `draw_boxes` (function, linha 246)
- `draw_lines` (function, linha 254)
- `draw_player_hit_circle` (function, linha 262)
- `draw_range_circles` (function, linha 278)
- `draw_poison_gas_lines` (function, linha 306)
- `DebugClipRecorder` (class, linha 332)
- `DebugClipRecorder.__init__` (function, linha 333)
- `DebugClipRecorder.update` (function, linha 347)
- `DebugClipRecorder.write_frame` (function, linha 380)
- `DebugClipRecorder.prune_pending_frames` (function, linha 393)
- `DebugClipRecorder.flush_pending_frames` (function, linha 401)
- `DebugClipRecorder.start` (function, linha 406)
- `DebugClipRecorder.stop` (function, linha 421)
- `DebugClipRecorder.close` (function, linha 438)
- `draw_joystick_path_probe` (function, linha 442)
- `draw_debug_data` (function, linha 484)
- `run_viewer_worker` (function, linha 530)

## desktop.py

Imports: __future__, ctypes, os, pathlib, sys, threading, typing, webview, werkzeug.serving

- `console_log_path` (function, linha 29)
- `hide_console` (function, linha 33)
- `_owns_console` (function, linha 57)
- `_redirect_standard_streams` (function, linha 63)
- `unblock_bundled_webview_binaries` (function, linha 93)
- `import_webview` (function, linha 135)
- `set_windows_app_id` (function, linha 148)
- `run_webview` (function, linha 167)

## detect.py

Imports: ast, cv2, entity_model, json, numpy, onnxruntime, os, threading, utils, warnings

- `_numpy_nms` (function, linha 27)
- `_normalize_yolo_output` (function, linha 62)
- `_postprocess_raw` (function, linha 99)
- `Detect` (class, linha 164)
- `Detect.__init__` (function, linha 167)
- `Detect.__init__.get_optimal_threads` (function, linha 170)
- `Detect._session_options` (function, linha 217)
- `Detect._cpu_session` (function, linha 234)
- `Detect.load_model` (function, linha 238)
- `Detect.preprocess_image` (function, linha 269)
- `Detect.postprocess` (function, linha 297)
- `Detect._semantic_tile_detections` (function, linha 336)
- `Detect.detect_objects` (function, linha 384)

## discord_bot.py

Imports: PIL, asyncio, discord, io, time, typing, utils, window_controller

- `DiscordBot` (class, linha 14)
- `DiscordBot.__init__` (function, linha 15)
- `DiscordBot.set_window_controller` (function, linha 31)
- `DiscordBot._extract_discord_id` (function, linha 35)
- `DiscordBot.get_authorized_user_id` (function, linha 44)
- `DiscordBot.get_configured_guild_id` (function, linha 48)
- `DiscordBot.get_configured_guild` (function, linha 59)
- `DiscordBot.require_authorized_user` (function, linha 66)
- `DiscordBot.sync_commands` (function, linha 84)
- `DiscordBot.register_events` (function, linha 94)
- `DiscordBot.register_events.on_ready` (function, linha 96)
- `DiscordBot.register_commands` (function, linha 112)
- `DiscordBot.register_commands.screenshot` (function, linha 117)
- `DiscordBot.register_commands.stop` (function, linha 149)
- `DiscordBot.register_commands.pause` (function, linha 208)
- `DiscordBot.register_commands.start` (function, linha 274)
- `DiscordBot.register_commands.status` (function, linha 288)
- `DiscordBot.register_commands.restart_brawl_stars` (function, linha 319)
- `DiscordBot.register_commands.view_queue` (function, linha 340)
- `DiscordBot.register_commands.add_to_queue` (function, linha 386)
- `DiscordBot.register_commands.remove_from_queue` (function, linha 429)
- `DiscordBot.register_commands.clear_queue` (function, linha 453)
- `DiscordBot.register_commands.activate_playstyle` (function, linha 469)
- `DiscordBot.register_commands.help_command` (function, linha 486)
- `DiscordBot.run_bot` (function, linha 498)

## entity_model.py

Imports: ast, numpy

- `read_layout` (function, linha 7)
- `decode_pose` (function, linha 20)

## lobby_automation.py

Imports: cv2, os, time, utils

- `LobbyAutomation` (class, linha 12)
- `LobbyAutomation.__init__` (function, linha 14)
- `LobbyAutomation.check_for_idle` (function, linha 23)
- `LobbyAutomation._should_interrupt` (function, linha 44)
- `LobbyAutomation._sleep_interruptible` (function, linha 50)
- `LobbyAutomation.select_brawler` (function, linha 58)

## main.py

Imports: adbutils, argparse, debug_view, desktop, inspect, lobby_automation, os, pathlib, play, profiles, socket, stage_manager, state_finder, sys, threading, time, time_management, tomllib, utils, webbrowser, webui, window_controller

- `_patched_getfile` (function, linha 10)
- `parse_cli_args` (function, linha 33)
- `_startup_project_root` (function, linha 77)
- `load_saved_interface_mode` (function, linha 83)
- `resolve_interface_mode` (function, linha 98)
- `apply_play_order` (function, linha 144)
- `pyla_main` (function, linha 158)
- `pyla_main.Main` (class, linha 159)
- `pyla_main.Main.__init__` (function, linha 160)
- `pyla_main.Main.update_trophy_observer` (function, linha 211)
- `pyla_main.Main.load_models` (function, linha 218)
- `pyla_main.Main.restart_brawl_stars` (function, linha 225)
- `pyla_main.Main.should_stop` (function, linha 242)
- `pyla_main.Main.should_pause` (function, linha 245)
- `pyla_main.Main.sleep_interruptible` (function, linha 248)
- `pyla_main.Main.stop_gracefully` (function, linha 258)
- `pyla_main.Main.start_state_checker` (function, linha 265)
- `pyla_main.Main.stop_state_checker` (function, linha 276)
- `pyla_main.Main.set_latest_state` (function, linha 281)
- `pyla_main.Main.get_latest_state` (function, linha 285)
- `pyla_main.Main.handle_detected_state` (function, linha 289)
- `pyla_main.Main.state_checker_loop` (function, linha 302)
- `pyla_main.Main.wait_while_paused` (function, linha 317)
- `pyla_main.Main.handle_pause_request` (function, linha 339)
- `pyla_main.Main.manage_time_tasks` (function, linha 344)
- `pyla_main.Main.check_and_handle_brawl_stars_crash` (function, linha 365)
- `pyla_main.Main.main` (function, linha 383)
- `find_open_port` (function, linha 499)
- `open_browser_later` (function, linha 508)
- `open_browser_later._open` (function, linha 509)
- `stop_on_window_close` (function, linha 517)
- `stop_on_window_close._on_close` (function, linha 519)
- `run_interface` (function, linha 529)

## match_logger.py

Imports: atexit, datetime, gzip, json, queue, secrets, threading, time, utils

- `_json_default` (function, linha 24)
- `_round_box` (function, linha 29)
- `MatchLogger` (class, linha 36)
- `MatchLogger.__init__` (function, linha 37)
- `MatchLogger.start` (function, linha 58)
- `MatchLogger.stop` (function, linha 75)
- `MatchLogger.shutdown` (function, linha 83)
- `MatchLogger.observe_state` (function, linha 93)
- `MatchLogger.log` (function, linha 107)
- `MatchLogger.log_touch` (function, linha 114)
- `MatchLogger.log_frame` (function, linha 120)
- `MatchLogger.detections_with_conf` (function, linha 129)
- `MatchLogger._writer` (function, linha 138)

## play.py

Imports: cv2, detect, match_logger, math, numpy, os, random, state_finder, time, utils

- `Play` (class, linha 23)
- `Play.__init__` (function, linha 27)
- `Play.get_entity_pos` (function, linha 111)
- `Play.get_distance` (function, linha 115)
- `Play.is_there_enemy` (function, linha 119)
- `Play.attack` (function, linha 124)
- `Play.use_hypercharge` (function, linha 127)
- `Play.use_gadget` (function, linha 135)
- `Play.use_super` (function, linha 143)
- `Play.get_random_movement` (function, linha 152)
- `Play.movement_to_vector` (function, linha 157)
- `Play.rotate_movement` (function, linha 171)
- `Play.movement_direction_key` (function, linha 181)
- `Play.unstuck_movement_if_needed` (function, linha 190)
- `Play.load_brawler_ranges` (function, linha 246)
- `Play.can_attack_through_walls` (function, linha 260)
- `Play.must_brawler_hold_attack` (function, linha 269)
- `Play.walls_block_line_of_sight` (function, linha 274)
- `Play.get_player_hit_circle` (function, linha 293)
- `Play.get_actual_player_box` (function, linha 301)
- `Play.point_rect_distance_sq` (function, linha 313)
- `Play.walls_block_swept_circle` (function, linha 321)
- `Play.is_enemy_hittable` (function, linha 358)
- `Play.enemy_targets` (function, linha 366)
- `Play.is_there_enemy_spawnable` (function, linha 371)
- `Play.find_closest_enemy_spawnable` (function, linha 374)
- `Play.is_enemy_spawnable` (function, linha 379)
- `Play.select_enemy_target` (function, linha 386)
- `Play.can_use_ability_on_enemy` (function, linha 390)
- `Play.find_closest_enemy` (function, linha 398)
- `Play.find_closest_teammate` (function, linha 425)
- `Play.is_there_poison_gas` (function, linha 436)
- `Play.get_main_data` (function, linha 497)
- `Play.is_path_blocked` (function, linha 501)
- `Play.validate_game_data` (function, linha 523)
- `Play.track_no_detections` (function, linha 542)
- `Play.do_movement` (function, linha 552)
- `Play.get_brawler_range` (function, linha 559)
- `Play.normalize_move` (function, linha 565)
- `Play.clamp_movement` (function, linha 572)
- `Play.loop` (function, linha 582)
- `Play.check_if_hypercharge_ready` (function, linha 654)
- `Play.check_if_gadget_ready` (function, linha 671)
- `Play.check_if_super_ready` (function, linha 688)
- `Play.offset_tile_data` (function, linha 706)
- `Play.get_tile_data` (function, linha 718)
- `Play.process_tile_data` (function, linha 724)
- `Play.get_movement` (function, linha 746)
- `Play.publish_debug_view` (function, linha 751)
- `Play.main` (function, linha 798)

## player_data.py

Imports: __future__, collections.abc, datetime, json, os, pathlib, re, requests, tempfile, threading, typing, utils

- `_BearerAuth` (class, linha 33)
- `_BearerAuth.__init__` (function, linha 36)
- `_BearerAuth.__call__` (function, linha 39)
- `PlayerDataError` (class, linha 44)
- `PlayerDataError.__init__` (function, linha 47)
- `normalize_player_tag` (function, linha 54)
- `OfficialBrawlStarsClient` (class, linha 68)
- `OfficialBrawlStarsClient.__init__` (function, linha 71)
- `OfficialBrawlStarsClient.credential_available` (function, linha 75)
- `OfficialBrawlStarsClient.fetch_player` (function, linha 78)
- `_parse_json` (function, linha 136)
- `_nonempty_name` (function, linha 149)
- `_stats_fields` (function, linha 155)
- `_snapshot_time` (function, linha 176)
- `_normalize_snapshot` (function, linha 194)
- `PlayerDataService` (class, linha 234)
- `PlayerDataService.__init__` (function, linha 237)
- `PlayerDataService.credential_available` (function, linha 249)
- `PlayerDataService._payload` (function, linha 252)
- `PlayerDataService._error_payload` (function, linha 271)
- `PlayerDataService.load` (function, linha 286)
- `PlayerDataService._save` (function, linha 306)
- `PlayerDataService.import_snapshot` (function, linha 326)
- `PlayerDataService.get` (function, linha 333)

## playstyles/skeleton.py

Imports: math, random, time, typing

- `time_now` (function, linha 12)
- `random_int` (function, linha 16)
- `must_brawler_hold_attack` (function, linha 101)
- `get_entity_pos` (function, linha 105)
- `get_actual_player_box` (function, linha 109)
- `get_distance` (function, linha 113)
- `get_brawler_range` (function, linha 117)
- `is_there_enemy` (function, linha 121)
- `attack` (function, linha 125)
- `use_hypercharge` (function, linha 129)
- `use_super` (function, linha 133)
- `use_gadget` (function, linha 137)
- `get_random_movement` (function, linha 141)
- `find_closest_enemy` (function, linha 145)
- `find_closest_teammate` (function, linha 157)
- `is_there_poison_gas` (function, linha 168)
- `is_path_blocked` (function, linha 172)
- `is_enemy_hittable` (function, linha 181)
- `rotate_movement` (function, linha 190)
- `is_there_enemy_spawnable` (function, linha 202)
- `find_closest_enemy_spawnable` (function, linha 207)
- `is_enemy_spawnable` (function, linha 212)

## profiles.py

Imports: __future__, contextlib, ctypes, datetime, fcntl, html.parser, json, msvcrt, os, pathlib, re, shutil, subprocess, sys, tempfile, threading, time, toml, unicodedata, urllib.parse, urllib.request, uuid

- `_atomic_json` (function, linha 43)
- `_FileLock` (class, linha 61)
- `_FileLock.__init__` (function, linha 64)
- `_FileLock.acquire` (function, linha 68)
- `_FileLock.release` (function, linha 90)
- `_profile_id` (function, linha 106)
- `_profile_name` (function, linha 112)
- `_link_or_copy` (function, linha 124)
- `_copy_tree` (function, linha 132)
- `_pid_alive` (function, linha 143)
- `_local_url` (function, linha 175)
- `_url_ready` (function, linha 187)
- `_UITokenParser` (class, linha 196)
- `_UITokenParser.handle_starttag` (function, linha 199)
- `_stop_runtime` (function, linha 205)
- `_stop_runtime.fetch` (function, linha 212)
- `ProfileManager` (class, linha 241)
- `ProfileManager.__init__` (function, linha 242)
- `ProfileManager._require_enabled` (function, linha 254)
- `ProfileManager._locked_registry` (function, linha 259)
- `ProfileManager._path` (function, linha 280)
- `ProfileManager._entry` (function, linha 286)
- `ProfileManager._running` (function, linha 294)
- `ProfileManager._view` (function, linha 310)
- `ProfileManager.list_profiles` (function, linha 326)
- `ProfileManager.get` (function, linha 332)
- `ProfileManager.create` (function, linha 336)
- `ProfileManager.launch` (function, linha 380)
- `ProfileManager.stop` (function, linha 417)
- `ProfileInstance` (class, linha 445)
- `ProfileInstance.__init__` (function, linha 448)
- `ProfileInstance.publish_url` (function, linha 460)
- `ProfileInstance.close` (function, linha 466)
- `bootstrap_profile` (function, linha 470)

## scrcpy/__init__.py

Imports: .const, .core


## scrcpy/const.py

Imports: 


## scrcpy/control.py

Imports: functools, scrcpy, socket, struct, time

- `inject` (function, linha 10)
- `inject.wrapper` (function, linha 18)
- `inject.wrapper.inner` (function, linha 20)
- `ControlSender` (class, linha 32)
- `ControlSender.__init__` (function, linha 33)
- `ControlSender.keycode` (function, linha 37)
- `ControlSender.text` (function, linha 51)
- `ControlSender.touch` (function, linha 63)
- `ControlSender.scroll` (function, linha 90)
- `ControlSender.back_or_turn_screen_on` (function, linha 113)
- `ControlSender.expand_notification_panel` (function, linha 123)
- `ControlSender.expand_settings_panel` (function, linha 130)
- `ControlSender.collapse_panels` (function, linha 137)
- `ControlSender.get_clipboard` (function, linha 143)
- `ControlSender.set_clipboard` (function, linha 170)
- `ControlSender.set_screen_power_mode` (function, linha 182)
- `ControlSender.rotate_device` (function, linha 192)
- `ControlSender.swipe` (function, linha 198)

## scrcpy/core.py

Imports: .const, .control, adbutils, av.codec, av.error, cv2, numpy, os, socket, struct, threading, time, typing

- `Client` (class, linha 24)
- `Client.__init__` (function, linha 25)
- `Client.__init_server_connection` (function, linha 107)
- `Client.__deploy_server` (function, linha 141)
- `Client.start` (function, linha 178)
- `Client.stop` (function, linha 201)
- `Client.__stream_loop` (function, linha 224)
- `Client.add_listener` (function, linha 257)
- `Client.remove_listener` (function, linha 267)
- `Client.__send_to_listeners` (function, linha 277)

## scripts/browser_audit.py

Imports: json, os, pathlib, playwright.sync_api, sys


## scripts/inventory.py

Imports: ast, hashlib, json, pathlib


## scripts/package_source.py

Imports: pathlib, sys, zipfile


## scripts/serve_audit.py

Imports: main, os, pathlib, sys, webui


## scripts/smoke_windows_exe.py

Imports: json, pathlib, re, subprocess, sys, time, urllib.error, urllib.request


## setup.py

Imports: glob, importlib, jaraco.functools, os, platform, setuptools, shutil, subprocess, sys, wheel

- `bootstrap` (function, linha 11)
- `get_requirement_name` (function, linha 30)
- `check_base_requirements` (function, linha 43)
- `get_gpu_info` (function, linha 65)

## stage_manager.py

Imports: cv2, state_finder, sys, threading, time, trophy_observer, utils

- `load_image` (function, linha 9)
- `StageManager` (class, linha 22)
- `StageManager.__init__` (function, linha 23)
- `StageManager._should_stop` (function, linha 61)
- `StageManager._should_pause` (function, linha 64)
- `StageManager._sleep_interruptible` (function, linha 67)
- `StageManager.validate_trophies` (function, linha 78)
- `StageManager.start_game` (function, linha 90)
- `StageManager.handle_daily_wins` (function, linha 162)
- `StageManager.click_star_drop` (function, linha 174)
- `StageManager.click_star_drop._handle_drop` (function, linha 178)
- `StageManager.end_game` (function, linha 190)
- `StageManager.quit_shop` (function, linha 260)
- `StageManager.close_pop_up` (function, linha 264)
- `StageManager.do_state` (function, linha 274)

## state_finder.py

Imports: cv2, os, sys, time, utils

- `is_template_in_region` (function, linha 27)
- `load_template` (function, linha 60)
- `find_game_result` (function, linha 82)
- `get_in_game_state` (function, linha 106)
- `is_in_shop` (function, linha 147)
- `is_in_brawler_selection` (function, linha 151)
- `is_in_offer_popup` (function, linha 155)
- `is_in_lobby` (function, linha 159)
- `is_in_end_of_a_match` (function, linha 163)
- `is_in_trophy_reward` (function, linha 167)
- `is_in_brawl_pass` (function, linha 171)
- `is_in_star_road` (function, linha 175)
- `is_in_match_making` (function, linha 179)
- `is_in_prestige_milestone` (function, linha 183)
- `is_in_star_drop` (function, linha 187)
- `is_underdog` (function, linha 197)
- `is_in_daily_wins` (function, linha 201)
- `get_state` (function, linha 205)

## tests/conftest.py

Imports: os, pathlib, pytest, shutil, sys, utils, webui

- `application` (function, linha 11)
- `client` (function, linha 31)
- `headers` (function, linha 35)

## tests/test_audit.py

Imports: asyncio, io, json, pytest, threading, time, types, unittest.mock, utils, webui.runtime, webui.services

- `test_local_read_routes` (function, linha 11)
- `test_session_and_origin_protection` (function, linha 16)
- `test_free_public_state_unchanged` (function, linha 22)
- `test_queue_crud_and_persistence` (function, linha 25)
- `test_duplicate_order_rejected` (function, linha 36)
- `test_invalid_json_shape_is_client_error` (function, linha 43)
- `test_malformed_json_is_client_error` (function, linha 46)
- `test_storage_failure_does_not_report_success` (function, linha 49)
- `test_storage_failure_does_not_report_success.fail` (function, linha 52)
- `test_failed_serialization_preserves_file` (function, linha 57)
- `test_invalid_settings_are_rejected` (function, linha 65)
- `test_settings_roundtrip_reset` (function, linha 69)
- `test_secret_mask_preserve_and_clear` (function, linha 75)
- `test_playstyle_import_activate_delete` (function, linha 84)
- `test_invalid_playstyle_cannot_break_bootstrap` (function, linha 95)
- `test_empty_playstyle_rejected` (function, linha 101)
- `test_invalid_history_dates` (function, linha 106)
- `test_empty_queue_start_and_stop` (function, linha 109)
- `test_discord_requires_explicit_authorized_user` (function, linha 114)
- `test_runtime_lifecycle_with_simulated_worker` (function, linha 121)
- `test_runtime_lifecycle_with_simulated_worker.worker` (function, linha 124)

## tests/test_discord_controls.py

Imports: asyncio, json, pytest, re, requests, types, unittest.mock, utils

- `offline_discord_controls` (function, linha 20)
- `offline_discord_controls.unexpected_network` (function, linha 24)
- `controls` (function, linha 32)
- `invoke_command` (function, linha 38)
- `test_control_commands_require_explicit_owner` (function, linha 54)
- `test_existing_controls_still_reject_other_users` (function, linha 68)
- `test_authorized_queue_crud_persists_and_preserves_progress` (function, linha 80)
- `test_authorized_queue_crud_persists_and_preserves_progress.scenario` (function, linha 85)
- `test_invalid_add_does_not_mutate_queue` (function, linha 120)
- `test_queue_controls_respect_runtime_edit_gate` (function, linha 128)
- `test_missing_queue_brawler_reports_failure` (function, linha 142)
- `test_authorized_playstyle_activation_persists` (function, linha 148)
- `test_invalid_playstyle_cannot_change_selection` (function, linha 159)
- `test_expected_service_failures_are_ephemeral` (function, linha 173)
- `test_help_matches_registered_commands_without_premium_promises` (function, linha 185)
- `test_add_slash_command_exposes_typed_target_and_choices` (function, linha 196)

## tests/test_local_features.py

Imports: debug_view, io, json, numpy

- `test_import_sort_data_and_push_all` (function, linha 8)
- `test_refresh_without_key_is_explicit_and_no_network` (function, linha 26)
- `test_invalid_import_preserves_previous_snapshot` (function, linha 31)
- `test_debug_controls_real_draw_and_roundtrip` (function, linha 36)
- `test_profile_api_creation` (function, linha 47)
- `test_new_routes_require_session` (function, linha 54)

## tests/test_models.py

Imports: detect, numpy, onnxruntime, pathlib, pytest, time, utils

- `test_bundled_model_cpu_inference` (function, linha 8)
- `test_actual_detect_pipeline` (function, linha 20)

## tests/test_player_data.py

Imports: json, player_data, pytest, requests

- `prohibit_external_requests` (function, linha 12)
- `prohibit_external_requests.forbidden_request` (function, linha 13)
- `official_player` (function, linha 18)
- `service` (function, linha 32)
- `test_official_json_import_maps_catalog_and_preserves_absent_fields` (function, linha 40)
- `test_local_format_import_accepts_object_or_json` (function, linha 65)
- `test_invalid_import_preserves_previous_snapshot` (function, linha 98)
- `test_malformed_tags_rejected_before_any_network` (function, linha 110)
- `test_missing_credential_is_explicit_and_never_invents_statistics` (function, linha 121)
- `test_cached_snapshot_needs_no_api_credential` (function, linha 130)
- `test_profiles_keep_separate_snapshots` (function, linha 141)
- `test_corrupt_persisted_snapshot_does_not_become_fake_player_data` (function, linha 152)
- `FakeResponse` (class, linha 160)
- `FakeResponse.__init__` (function, linha 161)
- `FakeResponse.iter_content` (function, linha 166)
- `FakeResponse.close` (function, linha 169)
- `FakeSession` (class, linha 173)
- `FakeSession.__init__` (function, linha 174)
- `FakeSession.get` (function, linha 179)
- `test_official_request_is_fixed_host_tls_verified_and_bounded` (function, linha 186)
- `test_official_bearer_auth_ignores_netrc_and_session_credentials` (function, linha 202)
- `test_official_bearer_auth_ignores_netrc_and_session_credentials.forbidden_netrc` (function, linha 208)
- `test_missing_official_credential_does_not_request` (function, linha 220)
- `test_upstream_status_errors_never_echo_response_or_secret` (function, linha 242)
- `test_upstream_network_exception_is_redacted` (function, linha 258)
- `test_invalid_upstream_response_is_rejected` (function, linha 270)
- `test_refresh_persists_official_snapshot_for_later_offline_use` (function, linha 279)
- `test_snapshot_for_different_tag_is_not_reused` (function, linha 293)
- `test_import_marks_local_origin_and_discards_unrelated_fields` (function, linha 303)
- `test_local_snapshot_timestamp_reports_age` (function, linha 314)
- `test_malformed_saved_source_is_reported_safely` (function, linha 327)
- `test_failed_atomic_replace_preserves_previous_snapshot` (function, linha 343)
- `test_failed_atomic_replace_preserves_previous_snapshot.fail_replace` (function, linha 350)

## tests/test_profiles.py

Imports: concurrent.futures, json, os, pathlib, profiles, pytest, subprocess, sys, toml, urllib.request

- `installation` (function, linha 20)
- `test_profiles_have_independent_writable_data_and_clear_notifications` (function, linha 70)
- `test_immutable_resources_fall_back_to_copy` (function, linha 98)
- `test_immutable_resources_fall_back_to_copy.unsupported` (function, linha 99)
- `test_profile_names_reject_paths_and_invalid_input` (function, linha 107)
- `test_ids_and_duplicate_names_are_validated` (function, linha 113)
- `test_child_cannot_create_nested_profiles` (function, linha 125)
- `test_symlink_paths_and_recursive_resources_are_rejected` (function, linha 137)
- `test_registry_writes_do_not_lose_concurrent_profiles` (function, linha 150)
- `test_registry_writes_do_not_lose_concurrent_profiles.create` (function, linha 151)
- `FakeProcess` (class, linha 159)
- `FakeProcess.__init__` (function, linha 160)
- `FakeProcess.poll` (function, linha 165)
- `FakeProcess.terminate` (function, linha 168)
- `FakeProcess.wait` (function, linha 171)
- `test_frozen_launch_uses_private_runtime_and_argv` (function, linha 175)
- `test_frozen_launch_uses_private_runtime_and_argv.popen` (function, linha 182)
- `test_real_source_children_are_isolated_ready_and_not_duplicated` (function, linha 206)
- `test_bootstrap_selects_root_before_app_imports_and_guards_duplicate` (function, linha 231)
- `test_readiness_requires_the_child_response_header` (function, linha 251)
- `test_readiness_requires_the_child_response_header.Response` (class, linha 252)
- `test_readiness_requires_the_child_response_header.Response.__enter__` (function, linha 255)
- `test_readiness_requires_the_child_response_header.Response.__exit__` (function, linha 257)
- `test_readiness_requires_the_child_response_header.Opener` (class, linha 259)
- `test_readiness_requires_the_child_response_header.Opener.open` (function, linha 260)
- `test_stop_leaves_an_active_or_unidentified_child_running` (function, linha 268)
- `test_stop_leaves_an_active_or_unidentified_child_running.popen` (function, linha 270)
- `test_stop_leaves_an_active_or_unidentified_child_running.still_playing` (function, linha 277)
- `test_source_launcher_preserves_virtualenv_interpreter` (function, linha 285)

## time_management.py

Imports: time, utils

- `TimeManagement` (class, linha 5)
- `TimeManagement.__init__` (function, linha 6)
- `TimeManagement.start` (function, linha 10)
- `TimeManagement.check_time` (function, linha 14)
- `TimeManagement.state_check` (function, linha 21)
- `TimeManagement.no_detections_check` (function, linha 24)
- `TimeManagement.idle_check` (function, linha 27)

## trophy_observer.py

Imports: csv, dataclasses, datetime, enum, os, requests, secrets, time, typing, utils

- `GameMode` (class, linha 13)
- `MatchResult` (class, linha 18)
- `ParsedGameResult` (class, linha 25)
- `TrophyObserver` (class, linha 32)
- `TrophyObserver._replace_when_available` (function, linha 44)
- `TrophyObserver.__init__` (function, linha 65)
- `TrophyObserver.win_streak_gain` (function, linha 97)
- `TrophyObserver.calc_lost_decrement` (function, linha 100)
- `TrophyObserver.calc_win_increment` (function, linha 106)
- `TrophyObserver.calc_draw_increment` (function, linha 112)
- `TrophyObserver.calc_showdown_delta` (function, linha 115)
- `TrophyObserver.load_history` (function, linha 121)
- `TrophyObserver.save_history` (function, linha 160)
- `TrophyObserver._atomic_save_history` (function, linha 163)
- `TrophyObserver._normalize_history_row` (function, linha 185)
- `TrophyObserver.parse_game_result` (function, linha 204)
- `TrophyObserver.add_trophies` (function, linha 245)
- `TrophyObserver.add_win` (function, linha 307)
- `TrophyObserver.change_trophies` (function, linha 313)
- `TrophyObserver.send_results_to_api` (function, linha 317)

## utils.py

Imports: PIL, ast, ctypes, cv2, early_access.early_access, hashlib, html, io, json, math, os, packaging, pathlib, random, requests, sys, tempfile, time, toml, traceback

- `ui_delay` (function, linha 24)
- `sleep_ui` (function, linha 32)
- `get_brawler_stats` (function, linha 36)
- `get_player_info` (function, linha 40)
- `_get_project_root` (function, linha 44)
- `resolve_project_path` (function, linha 55)
- `resolve_within` (function, linha 59)
- `resolve_playstyle_path` (function, linha 67)
- `load_toml_as_dict` (function, linha 75)
- `invalidate_toml_cache` (function, linha 88)
- `save_dict_as_toml` (function, linha 93)
- `_atomic_write_text` (function, linha 99)
- `count_hsv_pixels` (function, linha 128)
- `count_mask_pixels` (function, linha 146)
- `save_brawler_data` (function, linha 156)
- `load_brawler_data` (function, linha 164)
- `api_update_brawler_data` (function, linha 177)
- `clear_brawler_data` (function, linha 182)
- `clean_queue` (function, linha 188)
- `find_template_center` (function, linha 242)
- `load_brawlers_info` (function, linha 265)
- `update_brawlers_info` (function, linha 273)
- `get_brawler_list` (function, linha 278)
- `update_missing_brawlers_info` (function, linha 294)
- `get_brawler_info` (function, linha 311)
- `save_brawler_icon` (function, linha 322)
- `get_latest_version` (function, linha 356)
- `get_announcements` (function, linha 366)
- `check_version` (function, linha 380)
- `format_notification_status` (function, linha 393)
- `notify_user` (function, linha 417)
- `get_discord_link` (function, linha 526)
- `get_online_wall_model_hash` (function, linha 538)
- `calculate_sha256` (function, linha 548)
- `current_wall_model_is_latest` (function, linha 560)
- `get_latest_wall_model_file` (function, linha 571)
- `get_latest_wall_model_classes` (function, linha 583)
- `update_wall_model_classes` (function, linha 593)
- `cprint` (function, linha 607)
- `normalize_brawler_filename` (function, linha 616)
- `get_brawler_icon_path` (function, linha 620)
- `get_dpi_scale` (function, linha 639)
- `is_safe_ast` (function, linha 674)
- `interpret_pyla_code` (function, linha 699)
- `validate_playstyle_metadata` (function, linha 724)
- `load_pyla_script` (function, linha 737)
- `get_playstyles_list` (function, linha 754)
- `load_default_pyla_script` (function, linha 768)
- `hash_playstyle` (function, linha 774)
- `config_bool` (function, linha 778)
- `clamp` (function, linha 789)
- `normalize_move` (function, linha 799)
- `mask_secret` (function, linha 807)

## webui/__init__.py

Imports: .app


## webui/app.py

Imports: .runtime, .services, __future__, datetime, discord_bot, flask, hmac, logging, profiles, secrets, threading, urllib.parse, utils, werkzeug.exceptions

- `_SuppressRuntimeStatusPolling` (class, linha 20)
- `_SuppressRuntimeStatusPolling.filter` (function, linha 21)
- `_SuppressQueuePolling` (class, linha 28)
- `_SuppressQueuePolling.filter` (function, linha 29)
- `_SuppressAssetsGetting` (class, linha 36)
- `_SuppressAssetsGetting.filter` (function, linha 37)
- `_SupressHistoryPolling` (class, linha 43)
- `_SupressHistoryPolling.filter` (function, linha 44)
- `_SuppressWebhookPutting` (class, linha 51)
- `_SuppressWebhookPutting.filter` (function, linha 52)
- `_configure_request_logging` (function, linha 58)
- `_start_discord_bot_thread` (function, linha 73)
- `create_app` (function, linha 89)
- `create_app._parsed_request_host` (function, linha 112)
- `create_app._is_allowed_origin` (function, linha 118)
- `create_app.protect_local_control_api` (function, linha 134)
- `create_app.add_local_security_headers` (function, linha 169)
- `create_app.index` (function, linha 177)
- `create_app.bootstrap` (function, linha 184)
- `create_app.profiles_list` (function, linha 190)
- `create_app.profiles_create` (function, linha 194)
- `create_app.profiles_launch` (function, linha 200)
- `create_app.profiles_stop` (function, linha 207)
- `create_app.player_data` (function, linha 212)
- `create_app.refresh_player_data` (function, linha 216)
- `create_app.import_player_data` (function, linha 227)
- `create_app.push_all_queue` (function, linha 233)
- `create_app.handle_known_errors` (function, linha 239)
- `create_app.handle_unexpected_error` (function, linha 244)
- `create_app.get_queue` (function, linha 251)
- `create_app.add_queue` (function, linha 255)
- `create_app.import_queue` (function, linha 261)
- `create_app.update_queue_item` (function, linha 267)
- `create_app.reorder_queue` (function, linha 274)
- `create_app.clear_queue` (function, linha 280)
- `create_app.delete_queue_item` (function, linha 285)
- `create_app.get_playstyles` (function, linha 290)
- `create_app.import_playstyle` (function, linha 294)
- `create_app.delete_playstyle` (function, linha 299)
- `create_app.activate_playstyle` (function, linha 304)
- `create_app.import_settings` (function, linha 310)
- `create_app.get_adb_devices` (function, linha 315)
- `create_app.scan_adb_devices` (function, linha 319)
- `create_app.get_settings` (function, linha 324)
- `create_app.update_settings` (function, linha 328)
- `create_app.reset_settings` (function, linha 333)
- `create_app.runtime_start` (function, linha 337)
- `create_app.runtime_status` (function, linha 350)
- `create_app.runtime_pause` (function, linha 354)
- `create_app.runtime_stop` (function, linha 360)
- `create_app.runtime_logs` (function, linha 366)
- `create_app.clear_runtime_logs` (function, linha 370)
- `create_app.history` (function, linha 375)
- `create_app.brawler_icon` (function, linha 399)
- `create_app.support_asset` (function, linha 406)

## webui/runtime.py

Imports: __future__, collections, re, sys, threading, time, traceback, typing

- `ThreadFilterStream` (class, linha 16)
- `ThreadFilterStream.__init__` (function, linha 19)
- `ThreadFilterStream.write` (function, linha 25)
- `ThreadFilterStream.flush` (function, linha 48)
- `ThreadFilterStream.__getattr__` (function, linha 51)
- `RuntimeControl` (class, linha 64)
- `RuntimeControl.__init__` (function, linha 65)
- `RuntimeControl.request_pause` (function, linha 70)
- `RuntimeControl.resume` (function, linha 73)
- `RuntimeControl.request_stop` (function, linha 76)
- `RuntimeControl.should_stop` (function, linha 80)
- `RuntimeControl.should_pause` (function, linha 83)
- `RuntimeControl.mark_running` (function, linha 86)
- `RuntimeControl.mark_paused` (function, linha 89)
- `RuntimeManager` (class, linha 93)
- `RuntimeManager.__init__` (function, linha 94)
- `RuntimeManager._set_state` (function, linha 105)
- `RuntimeManager.configure_start_gate` (function, linha 109)
- `RuntimeManager.get_status` (function, linha 117)
- `RuntimeManager.start` (function, linha 132)
- `RuntimeManager.start_current_queue` (function, linha 157)
- `RuntimeManager._run_worker` (function, linha 181)
- `RuntimeManager.pause` (function, linha 208)
- `RuntimeManager.stop` (function, linha 224)
- `RuntimeManager.get_logs` (function, linha 254)
- `RuntimeManager.clear_logs` (function, linha 258)

## webui/services.py

Imports: __future__, concurrent.futures, csv, datetime, json, logging, math, packaging, pathlib, player_data, shutil, socket, threading, toml, traceback, typing, utils, werkzeug.utils, window_controller

- `get_brawler_stats` (function, linha 37)
- `get_player_info` (function, linha 41)
- `WebDataService` (class, linha 51)
- `WebDataService.__init__` (function, linha 123)
- `WebDataService._bool_from_string` (function, linha 134)
- `WebDataService._deserialize` (function, linha 137)
- `WebDataService._serialize` (function, linha 162)
- `WebDataService._select_fields` (function, linha 167)
- `WebDataService._apply_updates` (function, linha 174)
- `WebDataService._normalize_debug_settings` (function, linha 199)
- `WebDataService._load_config` (function, linha 205)
- `WebDataService._save_config` (function, linha 208)
- `WebDataService._load_startup_queue_if_enabled` (function, linha 211)
- `WebDataService.get_auth_state` (function, linha 230)
- `WebDataService.get_current_version` (function, linha 237)
- `WebDataService.get_latest_version_safe` (function, linha 240)
- `WebDataService.get_warnings` (function, linha 251)
- `WebDataService.get_announcements_safe` (function, linha 263)
- `WebDataService._resolve_brawler_catalog` (function, linha 277)
- `WebDataService.get_brawler_catalog` (function, linha 283)
- `WebDataService.normalize_queue_entry` (function, linha 293)
- `WebDataService._sorted_play_order_enabled` (function, linha 315)
- `WebDataService.get_queue_data` (function, linha 319)
- `WebDataService._assert_queue_editable` (function, linha 334)
- `WebDataService.save_queue_data` (function, linha 339)
- `WebDataService._sync_running_queue_from_saved_file` (function, linha 345)
- `WebDataService.import_queue_file` (function, linha 363)
- `WebDataService.add_or_update_queue_item` (function, linha 388)
- `WebDataService.delete_queue_item` (function, linha 401)
- `WebDataService.clear_queue` (function, linha 407)
- `WebDataService.reorder_queue` (function, linha 413)
- `WebDataService.save_queue_to_file` (function, linha 438)
- `WebDataService.push_all_to_default_target` (function, linha 443)
- `WebDataService.get_playstyles_payload` (function, linha 495)
- `WebDataService.activate_playstyle` (function, linha 517)
- `WebDataService.delete_playstyle` (function, linha 531)
- `WebDataService.import_playstyle` (function, linha 548)
- `WebDataService.get_settings_payload` (function, linha 589)
- `WebDataService.update_settings` (function, linha 613)
- `WebDataService.reset_settings` (function, linha 652)
- `WebDataService.get_player_info_payload` (function, linha 696)
- `WebDataService.import_player_data` (function, linha 699)
- `WebDataService._has_player_values` (function, linha 707)
- `WebDataService.get_match_history_payload` (function, linha 712)
- `WebDataService._parse_match_datetime` (function, linha 871)
- `WebDataService._parse_int` (function, linha 884)
- `WebDataService._build_match_history_response` (function, linha 891)
- `WebDataService.get_bootstrap_payload` (function, linha 924)
- `WebDataService.import_settings_from_folder` (function, linha 966)
- `WebDataService.scan_adb_devices` (function, linha 1033)
- `WebDataService._scan_adb_devices_unlocked` (function, linha 1041)
- `WebDataService._scan_adb_devices_unlocked.open_port` (function, linha 1049)
- `WebDataService._scan_adb_devices_unlocked.connect` (function, linha 1059)

## window_controller.py

Imports: adbutils, atexit, concurrent.futures, debug_view, math, random, scrcpy, threading, time, utils

- `restart_adb_server` (function, linha 19)
- `online_devices` (function, linha 32)
- `adb_device_port_sort_key` (function, linha 44)
- `discover_device` (function, linha 61)
- `discover_device._safe_connect` (function, linha 64)
- `discover_device._try` (function, linha 92)
- `WindowController` (class, linha 118)
- `WindowController.__init__` (function, linha 121)
- `WindowController.get_latest_frame` (function, linha 169)
- `WindowController.force_rediscover` (function, linha 175)
- `WindowController.reconnect_scrcpy` (function, linha 190)
- `WindowController.restart_brawl_stars` (function, linha 243)
- `WindowController.is_brawl_stars_running` (function, linha 250)
- `WindowController.screenshot` (function, linha 271)
- `WindowController.reset_to_default_resolution` (function, linha 302)
- `WindowController.touch_down` (function, linha 313)
- `WindowController.touch_move` (function, linha 329)
- `WindowController.touch_up` (function, linha 345)
- `WindowController.move` (function, linha 361)
- `WindowController.release_movement` (function, linha 385)
- `WindowController.click` (function, linha 391)
- `WindowController.press` (function, linha 405)
- `WindowController.type_text` (function, linha 413)
- `WindowController.swipe` (function, linha 430)
- `WindowController.close` (function, linha 451)
- `WindowController.stop_scrcpy_with_timeout` (function, linha 460)
- `WindowController.stop_scrcpy_with_timeout.stop_client` (function, linha 461)
