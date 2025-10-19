# Test Harnesses and Descriptions
## node_modules\@sinonjs\commons\lib\called-in-order.test.js
- **Line 31**: describe("calledInOrder", function () {
- **Line 44**: describe("given single array argument", function () {
- **Line 45**: describe("when stubs were called in expected order", function () {
- **Line 46**: it("returns true", function () {
- **Line 64**: describe("when stubs were called in unexpected order", function () {
- **Line 65**: it("returns false", function () {
- **Line 84**: describe("given multiple arguments", function () {
- **Line 85**: describe("when stubs were called in expected order", function () {
- **Line 86**: it("returns true", function () {
- **Line 103**: describe("when stubs were called in unexpected order", function () {
- **Line 104**: it("returns false", function () {
## node_modules\@sinonjs\commons\lib\class-name.test.js
- **Line 7**: describe("className", function () {
- **Line 8**: it("returns the class name of an instance", function () {
- **Line 18**: it("returns 'Object' for {}", function () {
- **Line 23**: it("returns null for an object that has no prototype", function () {
- **Line 29**: it("returns null for an object whose prototype was mangled", function () {
## node_modules\@sinonjs\commons\lib\deprecated.test.js
- **Line 11**: describe("deprecated", function () {
- **Line 12**: describe("defaultMsg", function () {
- **Line 13**: it("should return a string", function () {
- **Line 21**: describe("printWarning", function () {
- **Line 28**: describe("when `process.emitWarning` is defined", function () {
- **Line 29**: it("should call process.emitWarning with a msg", function () {
- **Line 35**: describe("when `process.emitWarning` is undefined", function () {
- **Line 44**: describe("when `console.info` is defined", function () {
- **Line 45**: it("should call `console.info` with a message", function () {
- **Line 51**: describe("when `console.info` is undefined", function () {
- **Line 52**: it("should call `console.log` with a message", function () {
- **Line 61**: describe("wrap", function () {
- **Line 70**: it("should return a wrapper function", function () {
- **Line 74**: it("should assign the prototype of the passed method", function () {
- **Line 79**: it("should not be assigned to the wrapped method", function () {
- **Line 92**: it("should call `printWarning` before invoking", function () {
- **Line 96**: it("should invoke the passed method with the given arguments", function () {
## node_modules\@sinonjs\commons\lib\every.test.js
- **Line 7**: describe("util/core/every", function () {
- **Line 8**: it("returns true when the callback function returns true for every element in an iterable", function () {
- **Line 17**: it("returns false when the callback function returns false for any element in an iterable", function () {
- **Line 26**: it("calls the given callback once for each item in an iterable until it returns false", function () {
## node_modules\@sinonjs\commons\lib\function-name.test.js
- **Line 8**: describe("function-name", function () {
- **Line 9**: it("should return empty string if func is falsy", function () {
- **Line 15**: it("should use displayName by default", function () {
- **Line 23**: it("should use name if displayName is not available", function () {
- **Line 31**: it("should fallback to string parsing", function () {
- **Line 44**: it("should not fail when a name cannot be found", function () {
- **Line 56**: it("should not fail when toString is undefined", function () {
- **Line 62**: it("should not fail when toString throws", function () {
## node_modules\@sinonjs\commons\lib\global.test.js
- **Line 6**: describe("global", function () {
- **Line 13**: it("is same as global", function () {
## node_modules\@sinonjs\commons\lib\index.test.js
- **Line 17**: describe("package", function () {
- **Line 20**: it(`should export a method named ${name}`, function () {
- **Line 27**: it(`should export an object property named ${name}`, function () {
## node_modules\@sinonjs\commons\lib\order-by-first-call.test.js
- **Line 8**: describe("orderByFirstCall", function () {
- **Line 9**: it("should order an Array of spies by the callId of the first call, ascending", function () {
## node_modules\@sinonjs\commons\lib\type-of.test.js
- **Line 6**: describe("typeOf", function () {
- **Line 7**: it("returns boolean", function () {
- **Line 11**: it("returns string", function () {
- **Line 15**: it("returns number", function () {
- **Line 19**: it("returns object", function () {
- **Line 23**: it("returns function", function () {
- **Line 32**: it("returns undefined", function () {
- **Line 36**: it("returns null", function () {
- **Line 40**: it("returns array", function () {
- **Line 44**: it("returns regexp", function () {
- **Line 48**: it("returns date", function () {
## node_modules\@sinonjs\commons\lib\value-to-string.test.js
- **Line 6**: describe("util/core/valueToString", function () {
- **Line 7**: it("returns string representation of an object", function () {
- **Line 13**: it("returns 'null' for literal null'", function () {
- **Line 17**: it("returns 'undefined' for literal undefined", function () {
## node_modules\@sinonjs\commons\lib\prototypes\copy-prototype-methods.test.js
- **Line 6**: describe("copyPrototypeMethods", function () {
- **Line 7**: it("does not throw for Map", function () {
## node_modules\@sinonjs\commons\lib\prototypes\index.test.js
- **Line 13**: describe("prototypes", function () {
- **Line 14**: describe(".array", function () {
- **Line 18**: describe(".function", function () {
- **Line 22**: describe(".map", function () {
- **Line 26**: describe(".object", function () {
- **Line 30**: describe(".set", function () {
- **Line 34**: describe(".string", function () {
- **Line 46**: it("should have all the methods of the origin prototype", function () {
## node_modules\gensync\test\index.test.js
- **Line 62**: describe("gensync({})", () => {
- **Line 63**: describe("option validation", () => {
- **Line 111**: describe("generator function metadata", () => {
- **Line 203**: describe("'sync' handler", async () => {
- **Line 223**: describe("'async' handler", async () => {
- **Line 243**: describe("'errback' sync handler", async () => {
- **Line 263**: describe("'errback' async handler", async () => {
- **Line 286**: describe("gensync(function* () {})", () => {
- **Line 411**: describe("gensync.all()", () => {
- **Line 463**: describe("gensync.race()", () => {
## src\components\ListeningIndicator.test.tsx
- **Line 5**: describe('ListeningIndicator', () => {
- **Line 6**: it('renders correctly when listening is true', () => {
- **Line 12**: it('renders correctly when listening is false', () => {
## src\components\SOSButton.test.tsx
- **Line 5**: describe('SOSButton', () => {
- **Line 6**: it('renders correctly and is accessible', () => {
- **Line 12**: it('calls onPress when pressed', () => {
- **Line 20**: it('is disabled when disabled prop is true', () => {
## tests\test_asr_enrichment.py
- **test_transcribe_returns_enriched_segments**: No description
- **test_to_scene_events_copies_metadata**: No description
## tests\test_audio_clients.py
- **test_asr_client_transcribe_bytes_parses_segments**: No description
- **test_tts_client_speak_uses_defaults_and_returns_audio**: No description
## tests\test_clinician_data_store.py
- **test_data_store_returns_latest_vital**: No description
- **test_data_store_handles_medication_queries**: No description
- **test_data_store_handles_lab_and_imaging**: No description
## tests\test_clinician_query.py
- **test_clinician_query_assistant_prioritizes_vital_updates**: No description
- **test_clinician_query_assistant_handles_missing_fields**: No description
## tests\test_dashboard_ws.py
- **test_dashboard_websocket_stream**: No description
## tests\test_discovery_pairing.py
- **test_pair_endpoint_returns_token_and_qr**: No description
## tests\test_generate_sbar_report.py
- **test_build_markdown_body_formats_updates**: No description
- **test_render_markdown_appends_critique_section**: No description
## tests\test_health_endpoints.py
- No test functions found
## tests\test_latency_observability.py
- **test_latency_observability_after_stress**: Confirms latency metrics were recorded after stress recovery tests ran.
1. Scrape /metrics or /metrics/summary for updated histogram values.
2. Check orchestrator_metrics.jsonl appended recent turn_* entries.
## tests\test_llm_client.py
- **TestLLMClient**: No description
- **test_ask_builds_chat_completion_payload**: No description
- **test_ask_includes_context_and_history**: No description
## tests\test_lmstudio_runtime.py
- **test_ensure_model_loaded_when_already_active**: No description
- **test_ensure_model_loaded_swaps_out_other_model**: No description
## tests\test_local_metrics.py
- **test_metrics_file_contains_required_events**: No description
- **test_metrics_are_monotonic_and_deidentified**: No description
## tests\test_local_security.py
- **test_security_artifacts_exist**: No description
- **test_turn_text_requires_valid_token**: No description
- **test_ui_token_env_matches_file**: No description
## tests\test_mobile_bridge.py
- No test functions found
## tests\test_protocol_ingest.py
- **TestProtocolIngestor**: No description
- **test_save_and_get_protocol**: No description
- **test_missing_protocol**: No description
## tests\test_registry_loader.py
- **test_registry_validates_all_topics**: No description
## tests\test_sbar_builder.py
- **TestSBAR**: No description
- **test_empty_sbar**: No description
- **test_partial_sbar**: No description
- **test_complete_sbar**: No description
## tests\test_sbar_chaos_harness.py
- **test_sbar_chaos_harness_produces_markdown_and_metrics**: No description
## tests\test_sbar_dashboard.py
- **test_api_runs_returns_data**: No description
- **test_run_file_endpoint_serves_markdown**: No description
- **test_dashboard_html**: No description
## tests\test_sbar_exporter.py
- **test_export_sbar_dataset_produces_yaml_and_jsonl**: No description
## tests\test_sbar_monitor.py
- **test_monitor_emits_on_significant_change**: No description
- **test_monitor_suppresses_when_llm_says_no_change**: No description
## tests\test_scene_harness.py
- **test_scene_harness_generates_reports**: No description
## tests\test_scene_player.py
- **test_load_scene_sorted**: No description
- **test_iter_scene_applies_start_offset**: No description
- **test_play_scene_invokes_callback**: No description
## tests\test_scene_scaffolder.py
- **test_scene_scaffolder_builds_prompts**: No description
## tests\test_sos_button_ui.py
- **test_sos_button_triggers_turn**: No description
## tests\test_stress_recovery.py
- No test functions found
## tests\test_turn_audio_smoke.py
- No test functions found
## tests\test_turn_text_smoke.py
- No test functions found
## tests\test_windows_orchestrator.py
- **test_windows_orchestrator**: No description
## venv\Lib\site-packages\adodbapi\test\test_adodbapi_dbapi20.py
- **test_nextset**: No description
- **test_setoutputsize**: No description
## venv\Lib\site-packages\aiohttp\test_utils.py
- **TestServer**: No description
- **TestClient**: A test client implementation.

To write functional tests for aiohttp based servers.
## venv\Lib\site-packages\annotated_types\test_cases.py
- No test functions found
## venv\Lib\site-packages\greenlet\tests\test_contextvars.py
- **test_context_propagated_by_context_run**: No description
- **test_context_propagated_by_setting_attribute**: No description
- **test_context_not_propagated**: No description
- **test_context_shared**: No description
- **test_break_ctxvars**: No description
- **test_not_broken_if_using_attribute_instead_of_context_run**: No description
- **test_context_assignment_while_running**: No description
- **test_context_assignment_different_thread**: No description
- **test_context_assignment_wrong_type**: No description
- **test_contextvars_errors**: No description
## venv\Lib\site-packages\greenlet\tests\test_cpp.py
- **test_exception_switch**: No description
- **test_unhandled_nonstd_exception_aborts**: No description
- **test_unhandled_std_exception_aborts**: No description
- **test_unhandled_std_exception_as_greenlet_function_aborts**: No description
- **test_unhandled_exception_in_greenlet_aborts**: No description
## venv\Lib\site-packages\greenlet\tests\test_extension_interface.py
- **test_switch**: No description
- **test_switch_kwargs**: No description
- **test_setparent**: No description
- **test_getcurrent**: No description
- **test_new_greenlet**: No description
- **test_raise_greenlet_dead**: No description
- **test_raise_greenlet_error**: No description
- **test_throw**: No description
- **test_non_traceback_param**: No description
- **test_instance_of_wrong_type**: No description
- **test_not_throwable**: No description
## venv\Lib\site-packages\greenlet\tests\test_gc.py
- **test_dead_circular_ref**: No description
- **test_circular_greenlet**: No description
- **test_inactive_ref**: No description
- **test_finalizer_crash**: No description
## venv\Lib\site-packages\greenlet\tests\test_generator.py
- **test_generator**: No description
## venv\Lib\site-packages\greenlet\tests\test_generator_nested.py
- **test_layered_genlets**: No description
- **test_permutations**: No description
- **test_genlet_simple**: No description
- **test_genlet_bad**: No description
- **test_nested_genlets**: No description
## venv\Lib\site-packages\greenlet\tests\test_greenlet.py
- **TestGreenlet**: No description
- **TestGreenletSetParentErrors**: No description
- **TestRepr**: No description
- **TestMainGreenlet**: No description
- **TestBrokenGreenlets**: No description
- **test_simple**: No description
- **test_switch_no_run_raises_AttributeError**: No description
- **test_throw_no_run_raises_AttributeError**: No description
- **test_parent_equals_None**: No description
- **test_run_equals_None**: No description
- **test_two_children**: No description
- **test_two_recursive_children**: No description
- **test_threads**: No description
- **test_exception**: No description
- **test_send_exception**: No description
- **test_dealloc**: No description
- **test_dealloc_catches_GreenletExit_throws_other**: No description
- **test_dealloc_other_thread**: No description
- **test_frame**: No description
- **test_thread_bug**: No description
- **test_switch_kwargs**: No description
- **test_switch_kwargs_to_parent**: No description
- **test_switch_to_another_thread**: No description
- **test_exc_state**: No description
- **test_instance_dict**: No description
- **test_running_greenlet_has_no_run**: No description
- **test_deepcopy**: No description
- **test_parent_restored_on_kill**: No description
- **test_parent_return_failure**: No description
- **test_throw_exception_not_lost**: No description
- **test_throw_to_dead_thread_doesnt_crash**: No description
- **test_throw_to_dead_thread_doesnt_crash_wait**: No description
- **test_recursive_startup**: No description
- **test_threaded_updatecurrent**: No description
- **test_dealloc_switch_args_not_lost**: No description
- **test_tuple_subclass**: No description
- **test_abstract_subclasses**: No description
- **test_implicit_parent_with_threads**: No description
- **test_issue_245_reference_counting_subclass_no_threads**: No description
- **test_issue_245_reference_counting_subclass_threads**: No description
- **test_falling_off_end_switches_to_unstarted_parent_raises_error**: No description
- **test_falling_off_end_switches_to_unstarted_parent_works**: No description
- **test_switch_to_dead_greenlet_with_unstarted_perverse_parent**: No description
- **test_switch_to_dead_greenlet_reparent**: No description
- **test_can_access_f_back_of_suspended_greenlet**: No description
- **test_get_stack_with_nested_c_calls**: No description
- **test_frames_always_exposed**: No description
- **test_threaded_reparent**: No description
- **test_unexpected_reparenting**: No description
- **test_unexpected_reparenting_thread_running**: No description
- **test_cannot_delete_parent**: No description
- **test_cannot_delete_parent_of_main**: No description
- **test_main_greenlet_parent_is_none**: No description
- **test_set_parent_wrong_types**: No description
- **test_trivial_cycle**: No description
- **test_trivial_cycle_main**: No description
- **test_deeper_cycle**: No description
- **test_main_while_running**: No description
- **test_main_in_background**: No description
- **test_initial**: No description
- **test_main_from_other_thread**: No description
- **test_dead**: No description
- **test_formatting_produces_native_str**: No description
- **test_main_greenlet_type_can_be_subclassed**: No description
- **test_main_greenlet_is_greenlet**: No description
- **test_failed_to_initialstub**: No description
- **test_failed_to_switch_into_running**: No description
- **test_failed_to_slp_switch_into_running**: No description
- **test_reentrant_switch_two_greenlets**: No description
- **test_reentrant_switch_three_greenlets**: No description
- **test_reentrant_switch_three_greenlets2**: No description
- **test_reentrant_switch_GreenletAlreadyStartedInPython**: No description
- **test_reentrant_switch_run_callable_has_del**: No description
## venv\Lib\site-packages\greenlet\tests\test_greenlet_trash.py
- **TestTrashCanReEnter**: No description
- **test_it**: No description
## venv\Lib\site-packages\greenlet\tests\test_leaks.py
- **TestLeaks**: No description
- **test_arg_refs**: No description
- **test_kwarg_refs**: No description
- **test_threaded_leak**: No description
- **test_threaded_adv_leak**: No description
- **test_issue251_killing_cross_thread_leaks_list**: No description
- **test_issue251_with_cleanup_disabled**: No description
- **test_issue251_issue252_need_to_collect_in_background**: No description
- **test_issue251_issue252_need_to_collect_in_background_cleanup_disabled**: No description
- **test_issue251_issue252_explicit_reference_not_collectable**: No description
- **test_untracked_memory_doesnt_increase**: No description
- **test_untracked_memory_doesnt_increase_unfinished_thread_dealloc_in_thread**: No description
- **test_untracked_memory_doesnt_increase_unfinished_thread_dealloc_in_main**: No description
## venv\Lib\site-packages\greenlet\tests\test_stack_saved.py
- **Test**: No description
- **test_stack_saved**: No description
## venv\Lib\site-packages\greenlet\tests\test_throw.py
- **test_class**: No description
- **test_val**: No description
- **test_kill**: No description
- **test_throw_goes_to_original_parent**: No description
- **test_non_traceback_param**: No description
- **test_instance_of_wrong_type**: No description
- **test_not_throwable**: No description
## venv\Lib\site-packages\greenlet\tests\test_tracing.py
- **TestGreenletTracing**: Tests of ``greenlet.settrace()``
- **TestPythonTracing**: Tests of the interaction of ``sys.settrace()``
with greenlet facilities.

NOTE: Most of this is probably CPython specific.
- **test_a_greenlet_tracing**: No description
- **test_b_exception_disables_tracing**: No description
- **test_set_same_tracer_twice**: No description
- **test_trace_events_trivial**: No description
- **test_trace_events_into_greenlet_func_already_set**: No description
- **test_trace_events_into_greenlet_subclass_already_set**: No description
- **test_trace_events_from_greenlet_func_sets_profiler**: No description
- **test_trace_events_from_greenlet_subclass_sets_profiler**: No description
- **test_trace_events_multiple_greenlets_switching**: No description
- **test_trace_events_multiple_greenlets_switching_siblings**: No description
## venv\Lib\site-packages\greenlet\tests\test_version.py
- **test_version**: No description
## venv\Lib\site-packages\greenlet\tests\test_weakref.py
- **test_dead_weakref**: No description
- **test_inactive_weakref**: No description
- **test_dealloc_weakref**: No description
## venv\Lib\site-packages\ifaddr\test_ifaddr.py
- **TestIfaddr**: Unittests for :mod:`ifaddr`.

There isn't much unit-testing that can be done without making assumptions
on the system or mocking of operating system APIs. So this just contains
a sanity check for the moment.
- **test_netifaces_compatibility**: No description
- **test_get_adapters_contains_localhost**: No description
## venv\Lib\site-packages\kivy\tests\test_animations.py
- **TestAnimation**: No description
- **TestSequence**: No description
- **TestRepetitiveSequence**: No description
- **TestParallel**: No description
- **test_start_animation**: No description
- **test_animation_duration_0**: No description
- **test_cancel_all**: No description
- **test_cancel_all_2**: No description
- **test_stop_animation**: No description
- **test_stop_all**: No description
- **test_stop_all_2**: No description
- **test_duration**: No description
- **test_transition**: No description
- **test_animated_properties**: No description
- **test_animated_instruction**: No description
- **test_weakref**: No description
- **test_cancel_all**: No description
- **test_cancel_all_2**: No description
- **test_stop_all**: No description
- **test_stop_all_2**: No description
- **test_count_events**: No description
- **test_have_properties_to_animate**: No description
- **test_animated_properties**: No description
- **test_transition**: No description
- **test_stop**: No description
- **test_count_events**: No description
- **test_have_properties_to_animate**: No description
- **test_cancel_property**: No description
- **test_animated_properties**: No description
- **test_transition**: No description
- **test_count_events**: No description
## venv\Lib\site-packages\kivy\tests\test_app.py
- **test_start_raw_app**: No description
- **test_start_app_with_kv**: No description
- **test_user_data_dir**: No description
- **test_directory**: No description
- **test_name**: No description
- **TestApp**: No description
- **TestApp**: No description
- **TestApp**: No description
- **TestApp**: No description
- **TestApp**: No description
- **TestApp**: No description
- **TestApp**: No description
- **TestKvApp**: No description
## venv\Lib\site-packages\kivy\tests\test_audio.py
- **test_length_simple**: No description
- **test_length_playing**: No description
- **test_length_stopped**: No description
## venv\Lib\site-packages\kivy\tests\test_benchmark.py
- **test_event_dispatcher_creation**: No description
- **test_widget_creation**: No description
- **test_kv_widget_creation**: No description
- **test_complex_kv_widget**: No description
- **test_property_creation**: No description
- **test_property_set**: No description
- **test_widget_empty_draw**: No description
- **test_widget_dispatch_touch**: No description
- **test_random_label_create**: No description
- **test_parse_kv**: No description
## venv\Lib\site-packages\kivy\tests\test_clipboard.py
- **test_clipboard_not_dummy**: No description
- **test_clipboard_paste**: No description
- **test_clipboard_copy**: No description
- **test_clipboard_copy_paste**: No description
- **test_clipboard_copy_paste_with_emoji**: No description
## venv\Lib\site-packages\kivy\tests\test_clock.py
- **test_schedule_once**: No description
- **test_schedule_once_twice**: No description
- **test_schedule_once_draw_after**: No description
- **test_schedule_once_draw_before**: No description
- **test_unschedule**: No description
- **test_unschedule_event**: No description
- **test_unschedule_after_tick**: No description
- **test_unschedule_draw**: No description
- **test_trigger_create**: No description
- **test_trigger_cancel**: No description
- **test_trigger_interval**: No description
- **test_trigger_decorator**: No description
- **test_trigger_decorator_cancel**: No description
- **test_exception_caught**: No description
- **test_exception_ignored**: No description
- **test_exception_caught_handler**: No description
- **test_clock_ended_callback**: No description
- **test_clock_ended_del_safe**: No description
- **test_clock_ended_raises**: No description
- **test_clock_ended_del_safe_raises**: No description
- **test_clock_stop_twice**: No description
- **test_clock_restart**: No description
- **test_clock_event_trigger_ref**: No description
## venv\Lib\site-packages\kivy\tests\test_compat.py
- **test_isclose**: No description
## venv\Lib\site-packages\kivy\tests\test_config.py
- **test_configparser_callbacks**: Test that the ConfigParser handles callbacks.
- **test_configparser_read**: Test that the ConfigParser can read a config file.
- **test_configparser_setdefaults**: Test the setdefaults method works as expected.
## venv\Lib\site-packages\kivy\tests\test_coverage.py
- **test_coverage_base**: No description
- **test_coverage_multiline_on_event**: No description
- **test_coverage_trigger_event**: No description
- **test_coverage_trigger_all**: No description
## venv\Lib\site-packages\kivy\tests\test_doc_gallery.py
- **test_parse_docstring_info**: No description
## venv\Lib\site-packages\kivy\tests\test_environ_cli.py
- **test_env_exist**: No description
- **test_env_not_exist**: No description
## venv\Lib\site-packages\kivy\tests\test_fbo_py2py3.py
- **test_fbo_get_pixel_color**: No description
## venv\Lib\site-packages\kivy\tests\test_filechooser.py
- **test_filechooserlistview**: No description
## venv\Lib\site-packages\kivy\tests\test_filechooser_unicode.py
- **test_filechooserlistview_unicode**: No description
## venv\Lib\site-packages\kivy\tests\test_fonts.py
- **test_unicode_name**: No description
## venv\Lib\site-packages\kivy\tests\test_garden.py
- **test_garden_import_module**: No description
## venv\Lib\site-packages\kivy\tests\test_graphics.py
- **test_graphics_main_thread**: No description
- **test_create_graphics_second_thread**: No description
- **test_change_graphics_second_thread**: No description
- **test_create**: No description
- **test_adjusted_size**: No description
- **test_adjusted_pos**: No description
- **test_bounded_properties**: No description
- **test_canvas_management**: No description
- **test_circle**: No description
- **test_ellipse**: No description
- **test_point**: No description
- **test_point_add**: No description
- **test_line_rounded_rectangle**: No description
- **test_smoothline_rounded_rectangle**: No description
- **test_enlarged_line**: No description
- **test_antialiasing_line**: No description
- **test_smoothrectangle**: No description
- **test_smoothroundedrectangle**: No description
- **test_smoothellipse**: No description
- **test_smoothtriangle**: No description
- **test_smoothquad**: No description
- **test_fbo_pixels**: No description
- **test_identity_creation**: No description
- **test_translate_creation**: No description
- **test_scale_creation**: No description
- **test_from_kv**: No description
## venv\Lib\site-packages\kivy\tests\test_graphics_svg.py
- **test_simple**: No description
- **test_scale**: No description
- **test_rotate**: No description
## venv\Lib\site-packages\kivy\tests\test_image.py
- **test_keep_data**: No description
- **test_save_into_bytesio**: No description
## venv\Lib\site-packages\kivy\tests\test_imageloader.py
- **test_ImageLoaderSDL2**: No description
- **test_ImageLoaderPIL**: No description
- **test_ImageLoaderPygame**: No description
- **test_ImageLoaderFFPy**: No description
- **test_ImageLoaderGIF**: No description
- **test_ImageLoaderDDS**: No description
- **test_ImageLoaderTex**: No description
- **test_ImageLoaderImageIO**: No description
- **test_missing_tests**: No description
- **test_internal_converter_2x1**: No description
- **test_internal_converter_3x1**: No description
- **test_internal_converter_1x3**: No description
## venv\Lib\site-packages\kivy\tests\test_invalid_lang.py
- **test_invalid_childname**: No description
- **test_invalid_childname_before**: No description
## venv\Lib\site-packages\kivy\tests\test_kivy_init.py
- **test_kivy_configure**: Test the kivy_configure calls the post_configuration callbacks.
- **test_kivy_get_includes**: Test that the `get_includes` function return a list of valid paths.
- **test_kivy_usage**: Test the kivy_usage command.
## venv\Lib\site-packages\kivy\tests\test_knspace.py
- **test_not_exists**: No description
- **test_not_exists_property**: No description
- **test_allow_none**: No description
- **test_name**: No description
- **test_proxy_ref**: No description
- **test_constructor**: No description
- **test_re_assign**: No description
- **test_simple**: No description
- **test_simple_multiple_names**: No description
- **test_simple_binding**: No description
- **test_simple_name_change**: No description
- **test_fork_string**: No description
- **test_fork**: No description
- **test_fork_binding**: No description
## venv\Lib\site-packages\kivy\tests\test_lang.py
- **test_invalid_indentation**: No description
- **test_invalid_indentation2**: No description
- **test_loading_failed_1**: No description
- **test_parser_numeric_1**: No description
- **test_parser_numeric_2**: No description
- **test_references**: No description
- **test_references_with_template**: No description
- **test_references_with_template_case_2**: No description
- **test_references_with_template_case_3**: No description
- **test_with_multiline**: No description
- **test_with_eight_spaces**: No description
- **test_with_one_space**: No description
- **test_with_two_spaces**: No description
- **test_property_trailingspace**: No description
- **test_kv_python_init**: No description
- **test_apply_rules**: No description
- **test_load_utf8**: No description
- **test_bind_fstring**: No description
- **test_bind_fstring_reference**: No description
- **test_bind_fstring_expressions**: No description
- **test_bind_fstring_expressions_should_not_bind**: No description
## venv\Lib\site-packages\kivy\tests\test_lang_complex.py
- **test_complex_rewrite**: No description
- **TestWidget**: No description
- **TestWidget2**: No description
## venv\Lib\site-packages\kivy\tests\test_lang_pre_process_and_post_process.py
- **TestKvEvents**: No description
- **test_pure_python_auto_binding**: No description
- **test_pure_python_callbacks**: No description
- **test_instantiate_from_kv**: No description
- **test_instantiate_from_kv_with_event**: No description
- **test_instantiate_from_kv_with_child**: No description
- **test_instantiate_from_kv_with_child_inherit**: No description
- **TestEventsBase**: No description
- **TestEventsPureAuto**: No description
- **TestEventsPure**: No description
- **TestEventsFromKV**: No description
- **TestEventsFromKVEvent**: No description
- **TestEventsFromKVChild**: No description
- **TestEventsFromKVChildInherit**: No description
## venv\Lib\site-packages\kivy\tests\test_logger.py
- **test_purge_logs**: No description
- **test_logger_history_size**: No description
- **test_trace_level**: Kivy logger defines a custom level of Trace.
- **test_trace_level_has_level_name**: No description
- **test_logging_does_not_deep_copy**: No description
- **test_colonsplittinglogrecord_with_colon**: No description
- **test_colonsplittinglogrecord_without_colon**: No description
- **test_uncoloredlogrecord_without_markup**: No description
- **test_uncoloredlogrecord_with_markup**: No description
- **test_coloredlogrecord_without_markup**: No description
- **test_coloredlogrecord_with_markup**: No description
- **test_kivyformatter_colon_no_color**: No description
- **test_kivyformatter_colon_color**: No description
- **test_kivy_log_mode_marker_on**: This is a test of the pytest markers.
This should only be invoked if the environment variable is appropriately set
(before pytest is run).

Also, tests that kivy.logger paid attention to the environment variable
- **test_kivy_log_mode_marker_off**: This is a test of the pytest markers.
This should only be invoked if the environment variable is properly set
(before pytest is run).

Also, tests that kivy.logger paid attention to the environment variable
- **test_third_party_handlers_work**: No description
- **test_kivy_mode_handlers**: No description
- **test_python_mode_handlers**: No description
- **test_mixed_mode_handlers**: No description
- **test_logger_fix_8345**: The test checks that the ConsoleHandler is not in the Logger
handlers list if stderr is None.  Test sets stderr to None,
if the Console handler is found, the test fails.
Pythonw and Pyinstaller 5.7+ (with console set to false) set stderr
to None.
## venv\Lib\site-packages\kivy\tests\test_metrics.py
- **test_metrics_scale_factors**: No description
## venv\Lib\site-packages\kivy\tests\test_module_inspector.py
- **test_activate_deactivate_bottom**: No description
- **test_activate_deactivate_top**: No description
- **test_widget_button**: No description
- **test_widget_popup**: No description
- **test_widget_multipopup**: No description
## venv\Lib\site-packages\kivy\tests\test_motion_event.py
- **TestMotionEvent**: No description
- **test_to_absolute_pos**: No description
- **test_to_absolute_pos_error**: No description
## venv\Lib\site-packages\kivy\tests\test_mouse_hover_event.py
- **test_no_event_on_cursor_leave**: No description
- **test_no_event_on_system_size**: No description
- **test_no_event_on_rotate**: No description
- **test_no_event_on_close**: No description
- **test_begin_event_on_cursor_enter**: No description
- **test_begin_event_on_mouse_pos**: No description
- **test_update_event_with_enter_and_mouse_pos**: No description
- **test_update_event_with_mouse_pos**: No description
- **test_update_event_on_rotate**: No description
- **test_update_event_on_system_size**: No description
- **test_end_event_on_cursor_leave**: No description
- **test_end_event_on_window_close**: No description
- **test_with_full_cycle_with_cursor_events**: No description
- **test_with_full_cycle_with_mouse_pos_and_on_close_event**: No description
- **test_begin_event_no_dispatch_through_on_touch_events**: No description
- **test_update_event_no_dispatch_through_on_touch_events**: No description
- **test_end_event_no_dispatch_through_on_touch_events**: No description
## venv\Lib\site-packages\kivy\tests\test_mouse_multitouchsim.py
- **test_multitouch_dontappear**: No description
- **test_multitouch_appear**: No description
- **test_multitouch_dot_lefttouch**: No description
- **test_multitouch_dot_leftmove**: No description
- **test_multitouch_dot_righttouch**: No description
- **test_multitouch_dot_rightmove**: No description
- **test_multitouch_on_demand_noscatter_lefttouch**: No description
- **test_multitouch_on_demand_noscatter_leftmove**: No description
- **test_multitouch_on_demand_noscatter_righttouch**: No description
- **test_multitouch_on_demand_noscatter_rightmove**: No description
- **test_multitouch_on_demand_scatter_lefttouch**: No description
- **test_multitouch_on_demand_scatter_leftmove**: No description
- **test_multitouch_on_demand_scatter_righttouch**: No description
- **test_multitouch_on_demand_scatter_rightmove**: No description
- **test_multitouch_disabled_lefttouch**: No description
- **test_multitouch_disabled_leftmove**: No description
- **test_multitouch_disabled_righttouch**: No description
- **test_multitouch_disabled_rightmove**: No description
## venv\Lib\site-packages\kivy\tests\test_multistroke.py
- **test_immediate**: No description
- **test_scheduling**: No description
- **test_scheduling_limits**: No description
- **test_parallel_recognize**: No description
- **test_timeout_case_1**: No description
- **test_timeout_case_2**: No description
- **test_priority_sorting**: No description
- **test_name_filter**: No description
- **test_numpoints_filter**: No description
- **test_numstrokes_filter**: No description
- **test_priority_filter**: No description
- **test_orientation_filter**: No description
- **test_resample**: No description
- **test_rotateby**: No description
- **test_transfer**: No description
- **test_export_import_case_1**: No description
- **test_export_import_case_2**: No description
- **test_protractor_invariant**: No description
- **test_protractor_bound**: No description
## venv\Lib\site-packages\kivy\tests\test_properties.py
- **test_base**: No description
- **test_observer**: No description
- **test_objectcheck**: No description
- **test_stringcheck**: No description
- **test_numericcheck**: No description
- **test_listcheck**: No description
- **test_dictcheck**: No description
- **test_propertynone**: No description
- **test_reference**: No description
- **test_reference_child_update**: No description
- **test_dict**: No description
- **test_bounded_numeric_property**: No description
- **test_bounded_numeric_property_error_value**: No description
- **test_bounded_numeric_property_error_handler**: No description
- **test_numeric_string_with_units_check**: No description
- **test_numeric_string_without_units**: No description
- **test_property_rebind**: No description
- **test_color_property**: No description
- **test_alias_property_without_setter**: No description
- **test_alias_property**: No description
- **test_alias_property_cache_true**: No description
- **test_alias_property_with_bind**: No description
- **test_alias_property_with_force_dispatch_true**: No description
- **test_alias_property_cache_true_with_bind**: No description
- **test_alias_property_cache_true_force_dispatch_true**: No description
- **test_dictproperty_is_none**: No description
- **test_listproperty_is_none**: No description
- **test_numeric_property_dp**: No description
- **test_variable_list_property_dp_default**: No description
- **test_variable_list_property_dp**: No description
- **test_property_duplicate_name**: No description
- **test_property_rename_duplicate**: No description
- **test_override_prop_inheritance**: No description
- **test_manually_create_property**: No description
- **test_inherit_property**: No description
- **test_unknown_property**: No description
- **test_known_property_multiple_inheritance**: No description
- **test_pass_other_typeerror**: No description
- **test_object_init_error**: No description
- **TestCls**: No description
## venv\Lib\site-packages\kivy\tests\test_resources.py
- **test_file**: No description
- **test_load_resource_cached**: No description
- **test_load_resource_not_cached**: No description
- **test_load_resource_not_found**: No description
- **test_timestamp_and_lastaccess**: No description
- **test_print_usage**: No description
## venv\Lib\site-packages\kivy\tests\test_rst_replace.py
- **test_rst_replace**: No description
## venv\Lib\site-packages\kivy\tests\test_screen.py
- **test_switch_to**: No description
- **test_switching_does_not_affect_a_list_of_screens**: No description
## venv\Lib\site-packages\kivy\tests\test_storage.py
- **test_dict_storage**: No description
- **test_dict_storage_nofolder**: No description
- **test_json_storage_nofolder**: No description
- **test_json_storage**: No description
- **test_redis_storage**: No description
## venv\Lib\site-packages\kivy\tests\test_uix_actionbar.py
- **test_1_openclose**: No description
- **test_2_switch**: No description
- **test_3_openpress**: No description
- **test_4_openmulti**: No description
## venv\Lib\site-packages\kivy\tests\test_uix_anchorlayout.py
- **test_anchorlayout_default**: No description
- **test_anchorlayout_x**: No description
- **test_anchorlayout_y**: No description
- **test_anchor_layout_xy**: No description
## venv\Lib\site-packages\kivy\tests\test_uix_asyncimage.py
- **test_remote_zipsequence**: No description
- **test_local_zipsequence**: No description
- **test_reload_asyncimage**: No description
## venv\Lib\site-packages\kivy\tests\test_uix_boxlayout.py
- **test_boxlayout_orientation**: No description
- **test_boxlayout_spacing**: No description
- **test_boxlayout_padding**: No description
- **test_boxlayout_padding_spacing**: No description
## venv\Lib\site-packages\kivy\tests\test_uix_bubble.py
- **test_no_content**: No description
- **test_add_remove_content**: No description
- **test_add_arbitrary_content**: No description
- **test_add_two_content_widgets_fails**: No description
- **test_add_content_with_buttons**: No description
- **test_bubble_layout_with_predefined_arrow_pos**: No description
- **test_bubble_layout_without_arrow**: No description
- **test_bubble_layout_with_flex_arrow_pos**: No description
## venv\Lib\site-packages\kivy\tests\test_uix_carousel.py
- **test_remove_widget**: No description
- **test_previous_and_next**: No description
## venv\Lib\site-packages\kivy\tests\test_uix_colorpicker.py
- **test_render**: No description
- **test_clicks**: No description
- **test_render**: No description
- **test_set_colour**: No description
## venv\Lib\site-packages\kivy\tests\test_uix_dropdown.py
- **TestApp**: No description
## venv\Lib\site-packages\kivy\tests\test_uix_gridlayout.py
- **test_create_idx_iter**: No description
- **test_create_idx_iter2**: No description
- **TestLayout_fixed_sized_children**: No description
- **test_gridlayout_get_max_widgets_cols_rows_None**: No description
- **test_gridlayout_get_max_widgets_rows_None**: No description
- **test_gridlayout_get_max_widgets_cols_None**: No description
- **test_gridlayout_get_max_widgets_with_rows_cols**: No description
- **test_rows_cols_sizes**: No description
- **test_1x1**: No description
- **test_3x1_lr**: No description
- **test_3x1_rl**: No description
- **test_1x3_tb**: No description
- **test_1x3_bt**: No description
- **test_2x2_lr_tb**: No description
- **test_2x2_lr_bt**: No description
- **test_2x2_rl_tb**: No description
- **test_2x2_rl_bt**: No description
- **test_2x2_tb_lr**: No description
- **test_2x2_tb_rl**: No description
- **test_2x2_bt_lr**: No description
- **test_2x2_bt_rl**: No description
## venv\Lib\site-packages\kivy\tests\test_uix_layout.py
- **test_instantiation**: No description
## venv\Lib\site-packages\kivy\tests\test_uix_modal.py
- **TestApp**: test app class. 
## venv\Lib\site-packages\kivy\tests\test_uix_recyclegridlayout.py
- **TestLayout_all_the_data_is_visible**: No description
- **TestLayout_only_a_part_of_the_data_is_visible**: No description
- **test_1x1**: No description
- **test_3x1_lr**: No description
- **test_3x1_rl**: No description
- **test_1x3_tb**: No description
- **test_1x3_bt**: No description
- **test_2x2_lr_tb**: No description
- **test_2x2_lr_bt**: No description
- **test_2x2_rl_tb**: No description
- **test_2x2_rl_bt**: No description
- **test_2x2_tb_lr**: No description
- **test_2x2_tb_rl**: No description
- **test_2x2_bt_lr**: No description
- **test_2x2_bt_rl**: No description
- **test_4x1_lr**: No description
- **test_4x1_rl**: No description
- **test_1x4_tb**: No description
- **test_1x4_bt**: No description
- **test_3x3_lr_tb**: No description
- **test_3x3_lr_bt**: No description
- **test_3x3_rl_tb**: No description
- **test_3x3_rl_bt**: No description
- **test_3x3_tb_lr**: No description
- **test_3x3_tb_rl**: No description
- **test_3x3_bt_lr**: No description
- **test_3x3_bt_rl**: No description
## venv\Lib\site-packages\kivy\tests\test_uix_relativelayout.py
- **test_relativelayout_on_touch_move**: No description
- **test_relativelayout_coordinates**: No description
## venv\Lib\site-packages\kivy\tests\test_uix_scrollview.py
- **test_scrollbar_horizontal**: No description
- **test_scrollbar_vertical**: No description
- **test_scrollbar_both**: No description
- **test_scrollbar_horizontal_margin**: No description
- **test_scrollbar_vertical_margin**: No description
- **test_scrollbar_both_margin**: No description
- **test_smooth_scroll_end**: No description
## venv\Lib\site-packages\kivy\tests\test_uix_settings.py
- **test_settings_create_json_panel_errors**: No description
## venv\Lib\site-packages\kivy\tests\test_uix_slider.py
- **test_slider_move**: No description
## venv\Lib\site-packages\kivy\tests\test_uix_stacklayout.py
- **test_stacklayout_no_children**: No description
- **test_stacklayout_default**: No description
- **test_stacklayout_fixed_size**: No description
- **test_stacklayout_orientation_btrl**: No description
- **test_stacklayout_orientation_rlbt**: No description
- **test_stacklayout_padding**: No description
- **test_stacklayout_spacing**: No description
- **test_stacklayout_overflow**: No description
- **test_stacklayout_nospace**: No description
## venv\Lib\site-packages\kivy\tests\test_uix_textinput.py
- **test_focusable_when_disabled**: No description
- **test_wordbreak**: No description
- **test_ime**: No description
- **test_text_validate**: No description
- **test_selection_enter_multiline**: No description
- **test_selection_enter_singleline**: No description
- **test_del**: No description
- **test_escape**: No description
- **test_no_shift_cursor_arrow_on_selection**: No description
- **test_cursor_movement_control**: No description
- **test_cursor_blink**: No description
- **test_visible_lines_range**: No description
- **test_keyboard_scroll**: No description
- **test_scroll_doesnt_move_cursor**: No description
- **test_vertical_scroll_doesnt_depend_on_lines_rendering**: No description
- **test_selectall_copy_paste**: No description
- **test_cutcopypastebubble_content**: No description
## venv\Lib\site-packages\kivy\tests\test_uix_translate_coordinates.py
- **test_to_local_and_to_parent__relative**: No description
- **test_to_local_and_to_parent__not_relative**: No description
- **test_to_window_and_to_widget**: No description
## venv\Lib\site-packages\kivy\tests\test_uix_videoplayer.py
- **TestApp**: No description
## venv\Lib\site-packages\kivy\tests\test_uix_widget.py
- **test_default_widgets**: No description
- **test_button_properties**: No description
- **test_slider_properties**: No description
- **test_image_properties**: No description
- **test_add_widget_index_0**: No description
- **test_add_widget_index_1**: No description
- **test_add_widget_index_2**: No description
- **test_widget_root_from_code_with_kv**: No description
## venv\Lib\site-packages\kivy\tests\test_utils.py
- **test_escape_markup**: No description
- **test_format_bytes_to_human**: No description
- **test_boundary**: No description
- **test_is_color_transparent**: No description
- **test_deprecated**: No description
- **test_SafeList_iterate**: No description
- **test_SafeList_iterate_reverse**: No description
- **test_SafeList_clear**: No description
- **test_get_random_color_fixed_alpha**: No description
- **test_get_random_color_random_alpha**: No description
- **test_get_hex_from_color_noalpha**: No description
- **test_get_hex_from_color_alpha**: No description
- **test_get_color_from_hex_noalpha**: No description
- **test_get_color_from_hex_alpha**: No description
- **test_strtotuple**: No description
- **test_QueryDict**: No description
- **test_intersection**: No description
- **test_difference**: No description
- **test_interpolate_solo**: No description
- **test_interpolate_multi**: No description
- **test_reify**: No description
- **test_Platform_android**: No description
- **test_Platform_android_with_p4a**: No description
- **test_Platform_android_with_android_argument**: No description
- **test_Platform_ios**: No description
- **test_Platform_win32**: No description
- **test_Platform_cygwin**: No description
- **test_Platform_linux2**: No description
- **test_Platform_darwin**: No description
- **test_Platform_freebsd**: No description
- **test_Platform_unknown**: No description
## venv\Lib\site-packages\kivy\tests\test_vector.py
- **test_initializer_oneparameter_as_list**: No description
- **test_initializer_oneparameter_as_int**: No description
- **test_initializer_twoparameters**: No description
- **test_initializer_noparameter**: No description
- **test_initializer_threeparameters**: No description
- **test_sum_twovectors**: No description
- **test_sum_inplace**: No description
- **test_sum_inplace_scalar**: No description
- **test_sum_scalar**: No description
- **test_sub_twovectors**: No description
- **test_sub_inplace**: No description
- **test_sub_scalar**: No description
- **test_sub_inplace_scalar**: No description
- **test_mul_twovectors**: No description
- **test_mul_inplace**: No description
- **test_mul_inplace_scalar**: No description
- **test_mul_scalar**: No description
- **test_rmul_list**: No description
- **test_rmul_scalar**: No description
- **test_div_twovectors**: No description
- **test_truediv_twovectors**: No description
- **test_truediv_scalar**: No description
- **test_div_inplace**: No description
- **test_div_inplace_scalar**: No description
- **test_div_scalar**: No description
- **test_rdiv_list**: No description
- **test_rdiv_scalar**: No description
- **test_sum_oversizedlist**: No description
- **test_negation**: No description
- **test_length**: No description
- **test_length_zerozero**: No description
- **test_length2**: No description
- **test_distance**: No description
- **test_distance2**: No description
- **test_normalize**: No description
- **test_normalize_zerovector**: No description
- **test_dot**: No description
- **test_angle**: No description
- **test_rotate**: No description
- **test_**: No description
- **test_inbbox**: No description
- **test_intersection_roundingerror**: No description
## venv\Lib\site-packages\kivy\tests\test_video.py
- **test_video_unload**: No description
## venv\Lib\site-packages\kivy\tests\test_weakmethod.py
- **test_weak_method_on_obj**: No description
- **test_weak_method_func**: No description
## venv\Lib\site-packages\kivy\tests\test_widget.py
- **test_add_remove_widget**: No description
- **test_invalid_add_widget**: No description
- **test_clear_widgets**: No description
- **test_clear_widgets_children**: No description
- **test_position**: No description
- **test_size**: No description
- **test_collision**: No description
- **test_export_to_png**: No description
- **test_disabled**: No description
## venv\Lib\site-packages\kivy\tests\test_widget_walk.py
- **test_walk_large_tree**: No description
- **test_walk_single**: No description
## venv\Lib\site-packages\kivy\tests\test_window_base.py
- **test_to_normalized_pos**: No description
- **test_window_opacity_property**: No description
- **test_window_opacity_clamping_positive**: No description
- **test_window_opacity_clamping_negative**: No description
## venv\Lib\site-packages\kivy\tests\test_window_info.py
- **test_window_info_nonzero**: No description
## venv\Lib\site-packages\kivy\tests\pyinstaller\test_pyinstaller.py
- **TestSimpleWidget**: No description
- **TestVideoWidget**: No description
- **test_project**: No description
- **test_packaging**: No description
- **test_packaged_project**: No description
## venv\Lib\site-packages\kivy\tests\test_issues\test_6315.py
- **test_tb_lr_stacklayout**: No description
## venv\Lib\site-packages\kivy\tests\test_issues\test_issue_1084.py
- No test functions found
## venv\Lib\site-packages\kivy\tests\test_issues\test_issue_1091.py
- **test_tb_lr_stacklayout**: No description
## venv\Lib\site-packages\kivy\tests\test_issues\test_issue_599.py
- **test_minmax**: No description
## venv\Lib\site-packages\kivy\tests\test_issues\test_issue_609.py
- **test_markup_pos**: No description
## venv\Lib\site-packages\kivy\tests\test_issues\test_issue_6909.py
- **test_log_handles_cp949**: No description
- **test_non_utf8_encoding_raises_exception**: No description
## venv\Lib\site-packages\kivy\tests\test_issues\test_issue_883.py
- **test_empty_markup**: No description
## venv\Lib\site-packages\kivy\tests\test_urlrequest\test_urlrequest_requests.py
- **TestCallbacks**: No description
- **test_on_success**: No description
- **test_on_success_with_finish**: No description
- **test_on_redirect**: No description
- **test_on_redirect_with_finish**: No description
- **test_on_error**: No description
- **test_on_error_with_finis**: No description
- **test_on_failure**: No description
- **test_on_failure_with_finish**: No description
- **test_on_progress**: No description
- **test_on_progress_with_finish**: No description
- **test_on_finish**: No description
- **test_auth_header**: No description
- **test_ca_file**: No description
## venv\Lib\site-packages\kivy\tests\test_urlrequest\test_urlrequest_urllib.py
- **test_callbacks**: No description
- **test_auth_header**: No description
- **test_auth_auto**: No description
- **test_ca_file**: Passing a `ca_file` should not crash on http scheme, refs #6946
## venv\Lib\site-packages\opentelemetry\semconv\_incubating\attributes\test_attributes.py
- **TestCaseResultStatusValues**: No description
- **TestSuiteRunStatusValues**: No description
## venv\Lib\site-packages\qrcode\tests\test_example.py
- **test_example**: No description
## venv\Lib\site-packages\qrcode\tests\test_qrcode.py
- **test_basic**: No description
- **test_large**: No description
- **test_invalid_version**: No description
- **test_invalid_border**: No description
- **test_overflow**: No description
- **test_add_qrdata**: No description
- **test_fit**: No description
- **test_mode_number**: No description
- **test_mode_alpha**: No description
- **test_regression_mode_comma**: No description
- **test_mode_8bit**: No description
- **test_mode_8bit_newline**: No description
- **test_make_image_with_wrong_pattern**: No description
- **test_mask_pattern_setter**: No description
- **test_qrcode_bad_factory**: No description
- **test_qrcode_factory**: No description
- **test_optimize**: No description
- **test_optimize_short**: No description
- **test_optimize_longer_than_data**: No description
- **test_optimize_size**: No description
- **test_qrdata_repr**: No description
- **test_print_ascii_stdout**: No description
- **test_print_ascii**: No description
- **test_print_tty_stdout**: No description
- **test_print_tty**: No description
- **test_get_matrix**: No description
- **test_get_matrix_border**: No description
- **test_negative_size_at_construction**: No description
- **test_negative_size_at_usage**: No description
## venv\Lib\site-packages\qrcode\tests\test_qrcode_pil.py
- **test_render_pil**: No description
- **test_render_pil_background**: No description
- **test_render_pil_with_rgb_color_tuples**: No description
- **test_render_with_pattern**: No description
- **test_render_styled_Image**: No description
- **test_render_styled_with_embedded_image**: No description
- **test_render_styled_with_embedded_image_path**: No description
- **test_render_styled_with_drawer**: No description
- **test_render_styled_with_mask**: No description
- **test_embedded_image_and_error_correction**: If an embedded image is specified, error correction must be the highest so the QR code is readable
- **test_shortcut**: No description
## venv\Lib\site-packages\qrcode\tests\test_qrcode_pypng.py
- **test_render_pypng**: No description
- **test_render_pypng_to_str**: No description
## venv\Lib\site-packages\qrcode\tests\test_qrcode_svg.py
- **test_render_svg**: No description
- **test_render_svg_path**: No description
- **test_render_svg_fragment**: No description
- **test_svg_string**: No description
- **test_render_svg_with_background**: No description
- **test_svg_circle_drawer**: No description
## venv\Lib\site-packages\qrcode\tests\test_release.py
- **test_invalid_data**: No description
- **test_not_qrcode**: No description
- **test_no_change**: No description
- **test_change**: No description
## venv\Lib\site-packages\qrcode\tests\test_script.py
- **test_isatty**: No description
- **test_piped**: No description
- **test_stdin**: No description
- **test_stdin_py3_unicodedecodeerror**: No description
- **test_optimize**: No description
- **test_factory**: No description
- **test_bad_factory**: No description
- **test_sys_argv**: No description
- **test_output**: No description
- **test_factory_drawer_none**: No description
- **test_factory_drawer_bad**: No description
- **test_factory_drawer**: No description
- **test_commas**: No description
## venv\Lib\site-packages\qrcode\tests\test_util.py
- **test_check_wrong_version**: No description
## venv\Lib\site-packages\sniffio\_tests\test_sniffio.py
- **test_basics_cvar**: No description
- **test_basics_tlocal**: No description
- **test_asyncio**: No description
- **test_curio**: No description
## venv\Lib\site-packages\sqlalchemy\testing\suite\test_cte.py
- **test_select_nonrecursive_round_trip**: No description
- **test_select_recursive_round_trip**: No description
- **test_insert_from_select_round_trip**: No description
- **test_update_from_round_trip**: No description
- **test_delete_from_round_trip**: No description
- **test_delete_scalar_subq_round_trip**: No description
- **test_values_named_via_cte**: No description
## venv\Lib\site-packages\sqlalchemy\testing\suite\test_ddl.py
- **test_create_table**: No description
- **test_create_table_schema**: No description
- **test_drop_table**: No description
- **test_underscore_names**: No description
- **test_add_table_comment**: No description
- **test_drop_table_comment**: No description
- **test_create_table_if_not_exists**: No description
- **test_create_index_if_not_exists**: No description
- **test_drop_table_if_exists**: No description
- **test_drop_index_if_exists**: No description
- **test_long_convention_name**: No description
## venv\Lib\site-packages\sqlalchemy\testing\suite\test_deprecations.py
- **test_plain_union**: No description
- **test_limit_offset_selectable_in_unions**: No description
- **test_order_by_selectable_in_unions**: No description
- **test_distinct_selectable_in_unions**: No description
- **test_limit_offset_aliased_selectable_in_unions**: No description
## venv\Lib\site-packages\sqlalchemy\testing\suite\test_dialect.py
- **test_do_ping**: No description
- **test_all_visit_methods_accept_kw**: No description
- **test_integrity_error**: No description
- **test_exception_with_non_ascii**: No description
- **test_default_isolation_level**: No description
- **test_non_default_isolation_level**: No description
- **test_all_levels**: No description
- **test_invalid_level_execution_option**: test for the new get_isolation_level_values() method
- **test_invalid_level_engine_param**: test for the new get_isolation_level_values() method
and support for the dialect-level 'isolation_level' parameter.
- **test_dialect_user_setting_is_restored**: No description
- **test_autocommit_on**: No description
- **test_autocommit_off**: No description
- **test_turn_autocommit_off_via_default_iso_level**: No description
- **test_autocommit_block**: No description
- **test_dialect_autocommit_is_restored**: test #10147
- **test_percent_sign_round_trip**: test that the DBAPI accommodates for escaped / nonescaped
percent signs in a way that matches the compiler
- **test_control_case**: No description
- **test_wont_work_wo_insert**: No description
- **test_schema_change_on_connect**: No description
- **test_schema_change_works_w_transactions**: No description
- **test_round_trip_same_named_column**: No description
- **test_standalone_bindparam_escape**: No description
- **test_standalone_bindparam_escape_expanding**: No description
- **test_insert_single**: No description
- **test_insert_many**: No description
- **test_update_single**: No description
- **test_update_many**: No description
- **test_delete_single**: No description
- **test_delete_many**: No description
## venv\Lib\site-packages\sqlalchemy\testing\suite\test_insert.py
- **test_autoincrement_on_insert**: No description
- **test_last_inserted_id**: No description
- **test_native_lastrowid_autoinc**: No description
- **test_no_results_for_non_returning_insert**: test another INSERT issue found during #10453
- **test_autoclose_on_insert**: No description
- **test_autoclose_on_insert_implicit_returning**: No description
- **test_empty_insert**: No description
- **test_empty_insert_multiple**: No description
- **test_insert_from_select_autoinc**: No description
- **test_insert_from_select_autoinc_no_rows**: No description
- **test_insert_from_select**: No description
- **test_insert_from_select_with_defaults**: No description
- **test_explicit_returning_pk_autocommit**: No description
- **test_explicit_returning_pk_no_autocommit**: No description
- **test_autoincrement_on_insert_implicit_returning**: No description
- **test_last_inserted_id_implicit_returning**: No description
- **test_insertmanyvalues_returning**: No description
- **test_insert_w_floats**: test #9701.

this tests insertmanyvalues as well as decimal / floating point
RETURNING types
- **test_imv_returning_datatypes**: test #9739, #9808 (similar to #9701).

this tests insertmanyvalues in conjunction with various datatypes.

These tests are particularly for the asyncpg driver which needs
most types to be explicitly cast for the new IMV format
## venv\Lib\site-packages\sqlalchemy\testing\suite\test_reflection.py
- **test_has_table**: No description
- **test_has_table_cache**: No description
- **test_has_table_schema**: No description
- **test_has_table_nonexistent_schema**: No description
- **test_has_table_view**: No description
- **test_has_table_temp_table**: No description
- **test_has_table_temp_view**: No description
- **test_has_table_view_schema**: No description
- **test_has_index**: No description
- **test_has_index_schema**: No description
- **test_fk_ref**: tests for #10275
- **test_reflect_identity**: No description
- **test_reflect_comments**: No description
- **test_reflect_identity**: No description
- **test_reflect_comments**: No description
- **test_get_table_options**: No description
- **test_get_view_definition**: No description
- **test_get_columns**: No description
- **test_get_pk_constraint**: No description
- **test_get_foreign_keys**: No description
- **test_get_indexes**: No description
- **test_get_unique_constraints**: No description
- **test_get_table_comment**: No description
- **test_get_check_constraints**: No description
- **test_get_schema_names**: No description
- **test_has_schema**: No description
- **test_get_schema_names_w_translate_map**: test #7300
- **test_has_schema_w_translate_map**: No description
- **test_schema_cache**: No description
- **test_dialect_initialize**: No description
- **test_get_default_schema_name**: No description
- **test_get_table_names**: No description
- **test_get_view_names**: No description
- **test_get_temp_table_names**: No description
- **test_get_temp_view_names**: No description
- **test_get_comments**: No description
- **test_get_comments_with_schema**: No description
- **test_get_columns**: No description
- **test_reflect_table_temp_table**: No description
- **test_get_temp_table_columns**: No description
- **test_get_temp_view_columns**: No description
- **test_get_pk_constraint**: No description
- **test_get_foreign_keys**: No description
- **test_get_inter_schema_foreign_keys**: No description
- **test_get_indexes**: No description
- **test_get_noncol_index**: No description
- **test_get_temp_table_unique_constraints**: No description
- **test_get_temp_table_indexes**: No description
- **test_get_unique_constraints**: No description
- **test_get_view_definition**: No description
- **test_get_view_definition_does_not_exist**: No description
- **test_autoincrement_col**: test that 'autoincrement' is reflected according to sqla's policy.

Don't mark this test as unsupported for any backend !

(technically it fails with MySQL InnoDB since "id" comes before "id2")

A backend is better off not returning "autoincrement" at all,
instead of potentially returning "False" for an auto-incrementing
primary key column.
- **test_get_table_options**: No description
- **test_multi_get_table_options**: No description
- **test_multi_get_table_options_tables**: No description
- **test_get_multi_table_comment**: No description
- **test_get_multi_columns**: No description
- **test_get_multi_pk_constraint**: No description
- **test_get_multi_foreign_keys**: No description
- **test_get_multi_indexes**: No description
- **test_get_multi_unique_constraints**: No description
- **test_get_multi_check_constraints**: No description
- **test_not_existing_table**: No description
- **test_unreflectable**: No description
- **test_metadata**: No description
- **test_comments_unicode**: No description
- **test_comments_unicode_full**: No description
- **test_reflect_table_no_columns**: No description
- **test_get_columns_table_no_columns**: No description
- **test_reflect_incl_table_no_columns**: No description
- **test_reflect_view_no_columns**: No description
- **test_get_columns_view_no_columns**: No description
- **test_check_constraint_no_constraint**: No description
- **test_check_constraint_inline**: No description
- **test_check_constraint_standalone**: No description
- **test_check_constraint_mixed**: No description
- **test_index_column_order**: test for #12894
- **test_reflect_expression_based_indexes**: No description
- **test_reflect_covering_index**: No description
- **test_numeric_reflection**: No description
- **test_string_length_reflection**: No description
- **test_nullable_reflection**: No description
- **test_get_foreign_key_options**: No description
- **test_server_defaults**: No description
- **test_reflect_lowercase_forced_tables**: No description
- **test_get_table_names**: No description
- **test_computed_col_default_not_set**: No description
- **test_get_column_returns_computed**: No description
- **test_get_column_returns_persisted**: No description
- **test_get_column_returns_persisted_with_schema**: No description
- **test_reflect_identity**: No description
- **test_reflect_identity_schema**: No description
- **test_pk_column_order**: No description
- **test_fk_column_order**: No description
## venv\Lib\site-packages\sqlalchemy\testing\suite\test_results.py
- **test_via_attr**: No description
- **test_via_string**: No description
- **test_via_int**: No description
- **test_via_col_object**: No description
- **test_row_with_dupe_names**: No description
- **test_row_w_scalar_select**: test that a scalar select as a column is returned as such
and that type conversion works OK.

(this is half a SQLAlchemy Core test and half to catch database
backends that may have unusual behavior with scalar selects.)
- **test_single_roundtrip**: No description
- **test_executemany_roundtrip**: No description
- **test_executemany_returning_roundtrip**: No description
- **test_ss_cursor_status**: No description
- **test_conn_option**: No description
- **test_stmt_enabled_conn_option_disabled**: No description
- **test_aliases_and_ss**: No description
- **test_roundtrip_fetchall**: No description
- **test_roundtrip_fetchmany**: No description
## venv\Lib\site-packages\sqlalchemy\testing\suite\test_rowcount.py
- **test_basic**: No description
- **test_non_rowcount_scenarios_no_raise**: No description
- **test_update_rowcount1**: No description
- **test_update_rowcount2**: No description
- **test_update_delete_rowcount_return_defaults**: note this test should succeed for all RETURNING backends
as of 2.0.  In
Idf28379f8705e403a3c6a937f6a798a042ef2540 we changed rowcount to use
len(rows) when we have implicit returning
- **test_raw_sql_rowcount**: No description
- **test_text_rowcount**: No description
- **test_delete_rowcount**: No description
- **test_multi_update_rowcount**: No description
- **test_multi_delete_rowcount**: No description
## venv\Lib\site-packages\sqlalchemy\testing\suite\test_select.py
- **test_collate_order_by**: No description
- **test_plain**: No description
- **test_composed_int**: No description
- **test_composed_multiple**: No description
- **test_plain_desc**: No description
- **test_composed_int_desc**: No description
- **test_group_by_composed**: No description
- **test_tuples**: No description
- **test_simple_limit**: No description
- **test_limit_render_multiple_times**: No description
- **test_simple_fetch**: No description
- **test_simple_offset**: No description
- **test_simple_limit_offset**: No description
- **test_simple_fetch_offset**: No description
- **test_fetch_offset_no_order**: No description
- **test_simple_offset_zero**: No description
- **test_limit_offset_nobinds**: test that 'literal binds' mode works - no bound params.
- **test_fetch_offset_nobinds**: test that 'literal binds' mode works - no bound params.
- **test_bound_limit**: No description
- **test_bound_offset**: No description
- **test_bound_limit_offset**: No description
- **test_bound_fetch_offset**: No description
- **test_expr_offset**: No description
- **test_expr_limit**: No description
- **test_expr_limit_offset**: No description
- **test_expr_fetch_offset**: No description
- **test_simple_limit_expr_offset**: No description
- **test_expr_limit_simple_offset**: No description
- **test_simple_fetch_ties**: No description
- **test_fetch_offset_ties**: No description
- **test_fetch_offset_ties_exact_number**: No description
- **test_simple_fetch_percent**: No description
- **test_fetch_offset_percent**: No description
- **test_simple_fetch_percent_ties**: No description
- **test_fetch_offset_percent_ties**: No description
- **test_simple_join_both_tables**: No description
- **test_simple_join_whereclause_only**: No description
- **test_subquery**: No description
- **test_inner_join_fk**: No description
- **test_inner_join_true**: No description
- **test_inner_join_false**: No description
- **test_outer_join_false**: No description
- **test_outer_join_fk**: No description
- **test_plain_union**: No description
- **test_select_from_plain_union**: No description
- **test_limit_offset_selectable_in_unions**: No description
- **test_order_by_selectable_in_unions**: No description
- **test_distinct_selectable_in_unions**: No description
- **test_limit_offset_in_unions_from_alias**: No description
- **test_limit_offset_aliased_selectable_in_unions**: No description
- **test_compile**: No description
- **test_compile_literal_binds**: No description
- **test_execute**: No description
- **test_execute_expanding_plus_literal_execute**: No description
- **test_execute_tuple_expanding_plus_literal_execute**: No description
- **test_execute_tuple_expanding_plus_literal_heterogeneous_execute**: No description
- **test_multiple_empty_sets_bindparam**: No description
- **test_multiple_empty_sets_direct**: No description
- **test_empty_heterogeneous_tuples_bindparam**: No description
- **test_empty_heterogeneous_tuples_direct**: No description
- **test_empty_homogeneous_tuples_bindparam**: No description
- **test_empty_homogeneous_tuples_direct**: No description
- **test_bound_in_scalar_bindparam**: No description
- **test_bound_in_scalar_direct**: No description
- **test_nonempty_in_plus_empty_notin**: No description
- **test_empty_in_plus_notempty_notin**: No description
- **test_typed_str_in**: test related to #7292.

as a type is given to the bound param, there is no ambiguity
to the type of element.
- **test_untyped_str_in**: test related to #7292.

for untyped expression, we look at the types of elements.
Test for Sequence to detect tuple in.  but not strings or bytes!
as always....
- **test_bound_in_two_tuple_bindparam**: No description
- **test_bound_in_two_tuple_direct**: No description
- **test_bound_in_heterogeneous_two_tuple_bindparam**: No description
- **test_bound_in_heterogeneous_two_tuple_direct**: No description
- **test_bound_in_heterogeneous_two_tuple_text_bindparam**: No description
- **test_bound_in_heterogeneous_two_tuple_typed_bindparam_non_tuple**: No description
- **test_bound_in_heterogeneous_two_tuple_text_bindparam_non_tuple**: No description
- **test_empty_set_against_integer_bindparam**: No description
- **test_empty_set_against_integer_direct**: No description
- **test_empty_set_against_integer_negation_bindparam**: No description
- **test_empty_set_against_integer_negation_direct**: No description
- **test_empty_set_against_string_bindparam**: No description
- **test_empty_set_against_string_direct**: No description
- **test_empty_set_against_string_negation_bindparam**: No description
- **test_empty_set_against_string_negation_direct**: No description
- **test_null_in_empty_set_is_false_bindparam**: No description
- **test_null_in_empty_set_is_false_direct**: No description
- **test_startswith_unescaped**: No description
- **test_startswith_autoescape**: No description
- **test_startswith_sqlexpr**: No description
- **test_startswith_escape**: No description
- **test_startswith_autoescape_escape**: No description
- **test_endswith_unescaped**: No description
- **test_endswith_sqlexpr**: No description
- **test_endswith_autoescape**: No description
- **test_endswith_escape**: No description
- **test_endswith_autoescape_escape**: No description
- **test_contains_unescaped**: No description
- **test_contains_autoescape**: No description
- **test_contains_escape**: No description
- **test_contains_autoescape_escape**: No description
- **test_not_regexp_match**: No description
- **test_regexp_replace**: No description
- **test_regexp_match**: No description
- **test_select_all**: No description
- **test_select_columns**: No description
- **test_select_all**: No description
- **test_select_columns**: No description
- **test_insert_always_error**: No description
- **test_autoincrement_with_identity**: No description
- **test_select_exists**: No description
- **test_select_exists_false**: No description
- **test_distinct_on**: No description
- **test_is_or_is_not_distinct_from**: No description
- **test_window**: No description
- **test_window_rows_between**: No description
- **test_bitwise**: No description
## venv\Lib\site-packages\sqlalchemy\testing\suite\test_sequence.py
- **test_insert_roundtrip**: No description
- **test_insert_lastrowid**: No description
- **test_nextval_direct**: No description
- **test_optional_seq**: No description
- **test_insert_roundtrip_no_implicit_returning**: No description
- **test_insert_roundtrip_translate**: No description
- **test_nextval_direct_schema_translate**: No description
- **test_literal_binds_inline_compile**: No description
- **test_has_sequence**: No description
- **test_has_sequence_cache**: No description
- **test_has_sequence_other_object**: No description
- **test_has_sequence_schema**: No description
- **test_has_sequence_neg**: No description
- **test_has_sequence_schemas_neg**: No description
- **test_has_sequence_default_not_in_remote**: No description
- **test_has_sequence_remote_not_in_default**: No description
- **test_get_sequence_names**: No description
- **test_get_sequence_names_no_sequence_schema**: No description
- **test_get_sequence_names_sequences_schema**: No description
- **test_get_sequence_names_no_sequence**: No description
## venv\Lib\site-packages\sqlalchemy\testing\suite\test_types.py
- **test_round_trip**: No description
- **test_round_trip_executemany**: No description
- **test_literal**: No description
- **test_literal_non_ascii**: No description
- **test_empty_strings_varchar**: No description
- **test_null_strings_varchar**: No description
- **test_empty_strings_text**: No description
- **test_null_strings_text**: No description
- **test_array_roundtrip**: No description
- **test_literal_simple**: No description
- **test_literal_complex**: No description
- **test_binary_roundtrip**: No description
- **test_pickle_roundtrip**: No description
- **test_text_roundtrip**: No description
- **test_text_empty_strings**: No description
- **test_text_null_strings**: No description
- **test_literal**: No description
- **test_literal_non_ascii**: No description
- **test_literal_quoting**: No description
- **test_literal_backslashes**: No description
- **test_literal_percentsigns**: No description
- **test_nolength_string**: No description
- **test_literal**: No description
- **test_literal_non_ascii**: No description
- **test_dont_truncate_rightside**: No description
- **test_literal_quoting**: No description
- **test_literal_backslashes**: No description
- **test_concatenate_binary**: dialects with special string concatenation operators should
implement visit_concat_op_binary() and visit_concat_op_clauselist()
in their compiler.

.. versionchanged:: 2.0  visit_concat_op_clauselist() is also needed
   for dialects to override the string concatenation operator.
- **test_concatenate_clauselist**: dialects with special string concatenation operators should
implement visit_concat_op_binary() and visit_concat_op_clauselist()
in their compiler.

.. versionchanged:: 2.0  visit_concat_op_clauselist() is also needed
   for dialects to override the string concatenation operator.
- **test_literal**: No description
- **test_select_direct_literal_interval**: No description
- **test_arithmetic_operation_literal_interval**: No description
- **test_arithmetic_operation_table_interval_and_literal_interval**: No description
- **test_arithmetic_operation_table_date_and_literal_interval**: No description
- **test_round_trip**: No description
- **test_round_trip_decorated**: No description
- **test_null**: No description
- **test_literal**: No description
- **test_null_bound_comparison**: No description
- **test_select_direct**: No description
- **test_select_direct**: No description
- **test_select_direct**: No description
- **test_select_direct**: No description
- **test_select_direct**: No description
- **test_select_direct**: No description
- **test_select_direct**: No description
- **test_select_direct**: No description
- **test_select_direct**: No description
- **test_select_direct**: No description
- **test_literal**: No description
- **test_huge_int_auto_accommodation**: test #7909
- **test_huge_int**: No description
- **test_special_type**: No description
- **test_truediv_integer**: test #4926
- **test_floordiv_integer**: test #4926
- **test_truediv_numeric**: test #4926
- **test_truediv_float**: test #4926
- **test_floordiv_numeric**: test #4926
- **test_truediv_integer_bound**: test #4926
- **test_floordiv_integer_bound**: test #4926
- **test_render_literal_numeric**: No description
- **test_render_literal_numeric_asfloat**: No description
- **test_render_literal_float**: No description
- **test_float_custom_scale**: No description
- **test_numeric_as_decimal**: No description
- **test_numeric_as_float**: No description
- **test_infinity_floats**: test for #977, #7283
- **test_numeric_null_as_decimal**: No description
- **test_numeric_null_as_float**: No description
- **test_float_as_decimal**: No description
- **test_float_as_float**: No description
- **test_float_coerce_round_trip**: No description
- **test_decimal_coerce_round_trip**: No description
- **test_decimal_coerce_round_trip_w_cast**: No description
- **test_precision_decimal**: No description
- **test_enotation_decimal**: test exceedingly small decimals.

Decimal reports values with E notation when the exponent
is greater than 6.
- **test_enotation_decimal_large**: test exceedingly large decimals.
- **test_many_significant_digits**: No description
- **test_numeric_no_decimal**: No description
- **test_float_is_not_numeric**: No description
- **test_render_literal_bool**: No description
- **test_round_trip**: No description
- **test_null**: No description
- **test_whereclause**: No description
- **test_round_trip_data1**: No description
- **test_round_trip_pretty_large_data**: No description
- **test_index_typed_access**: No description
- **test_index_typed_comparison**: No description
- **test_path_typed_comparison**: No description
- **test_single_element_round_trip**: No description
- **test_round_trip_custom_json**: No description
- **test_round_trip_none_as_sql_null**: No description
- **test_round_trip_json_null_as_json_null**: No description
- **test_round_trip_none_as_json_null**: No description
- **test_unicode_round_trip**: No description
- **test_eval_none_flag_orm**: No description
- **test_string_cast_crit_spaces_in_key**: No description
- **test_string_cast_crit_simple_int**: No description
- **test_string_cast_crit_mixed_path**: No description
- **test_string_cast_crit_string_path**: No description
- **test_string_cast_crit_against_string_basic**: No description
- **test_round_trip**: No description
- **test_round_trip_executemany**: No description
- **test_round_trip_executemany_returning**: No description
- **test_uuid_round_trip**: No description
- **test_uuid_text_round_trip**: No description
- **test_literal_uuid**: No description
- **test_literal_text**: No description
- **test_literal_nonnative_uuid**: No description
- **test_literal_nonnative_text**: No description
- **test_uuid_returning**: No description
## venv\Lib\site-packages\sqlalchemy\testing\suite\test_unicode_ddl.py
- **test_insert**: No description
- **test_col_targeting**: No description
- **test_reflect**: No description
- **test_repr**: No description
## venv\Lib\site-packages\sqlalchemy\testing\suite\test_update_delete.py
- **test_update**: No description
- **test_delete**: No description
- **test_update_returning**: No description
- **test_delete_returning**: No description
## venv\Lib\site-packages\win32\test\test_clipboard.py
- **TestBitmap**: No description
- **TestStrings**: No description
- **TestGlobalMemory**: No description
- **test_722082**: No description
- **test_bitmap_roundtrip**: No description
- **test_unicode**: No description
- **test_unicode_text**: No description
- **test_string**: No description
- **test_mem**: No description
- **test_bad_mem**: No description
- **test_custom_mem**: No description
## venv\Lib\site-packages\win32\test\test_exceptions.py
- **TestBase**: No description
- **TestAPISimple**: No description
- **TestCOMSimple**: No description
- **testSimple**: No description
- **testErrnoIndex**: No description
- **testFuncIndex**: No description
- **testMessageIndex**: No description
- **testUnpack**: No description
- **testAsStr**: No description
- **testAsTuple**: No description
- **testClassName**: No description
- **testIdentity**: No description
- **testBaseClass**: No description
- **testAttributes**: No description
- **testStrangeArgsNone**: No description
- **testStrangeArgsNotEnough**: No description
- **testStrangeArgsTooMany**: No description
- **testIs**: No description
- **testSimple**: No description
- **testErrnoIndex**: No description
- **testMessageIndex**: No description
- **testAsStr**: No description
- **testAsTuple**: No description
- **testClassName**: No description
- **testIdentity**: No description
- **testBaseClass**: No description
- **testAttributes**: No description
- **testStrangeArgsNone**: No description
- **testStrangeArgsNotEnough**: No description
- **testStrangeArgsTooMany**: No description
## venv\Lib\site-packages\win32\test\test_odbc.py
- **TestStuff**: No description
- **test_insert_select**: No description
- **test_insert_select_unicode**: No description
- **test_insert_select_unicode_ext**: No description
- **testBit**: No description
- **testInt**: No description
- **testFloat**: No description
- **testVarchar**: No description
- **testLongVarchar**: Test a long text field in excess of internal cursor data size (65536)
- **testLongBinary**: Test a long raw field in excess of internal cursor data size (65536)
- **testRaw**: No description
- **test_widechar**: Test a unicode character that would be mangled if bound as plain character.
For example, previously the below was returned as ascii 'a'
- **testDates**: No description
- **test_set_nonzero_length**: No description
- **test_set_zero_length**: No description
- **test_set_zero_length_unicode**: No description
## venv\Lib\site-packages\win32\test\test_pywintypes.py
- **TestCase**: No description
- **testPyTimeFormat**: No description
- **testPyTimePrint**: No description
- **testTimeInDict**: No description
- **testPyTimeCompare**: No description
- **testPyTimeCompareOther**: No description
- **testTimeTuple**: No description
- **testTimeTuplems**: No description
- **testPyTimeFromTime**: No description
- **testPyTimeTooLarge**: No description
- **testGUID**: No description
- **testGUIDRichCmp**: No description
- **testGUIDInDict**: No description
## venv\Lib\site-packages\win32\test\test_security.py
- **TestDS**: No description
- **TestTranslate**: No description
- **testEqual**: No description
- **testNESID**: No description
- **testNEOther**: No description
- **testSIDInDict**: No description
- **testBuffer**: No description
- **testMemory**: No description
- **testDsGetDcName**: No description
- **testDsListServerInfo**: No description
- **testDsCrackNames**: No description
- **testDsCrackNamesSyntax**: No description
- **testTranslate1**: No description
- **testTranslate2**: No description
- **testTranslate3**: No description
- **testTranslate4**: No description
## venv\Lib\site-packages\win32\test\test_sspi.py
- **TestSSPI**: No description
- **testImpersonateKerberos**: No description
- **testImpersonateNTLM**: No description
- **testEncryptNTLM**: No description
- **testEncryptStreamNTLM**: No description
- **testEncryptKerberos**: No description
- **testEncryptStreamKerberos**: No description
- **testSignNTLM**: No description
- **testSignKerberos**: No description
- **testSequenceSign**: No description
- **testSequenceEncrypt**: No description
- **testSecBufferRepr**: No description
## venv\Lib\site-packages\win32\test\test_win32api.py
- **TestError**: No description
- **TestTime**: No description
- **testGetCurrentUser**: No description
- **testTimezone**: No description
- **test1**: No description
- **testValues**: No description
- **testNotifyChange**: No description
- **testShortLongPathNames**: No description
- **testShortUnicodeNames**: No description
- **testLongLongPathNames**: No description
- **test_FromString**: No description
- **test_last_error**: No description
- **testVkKeyScan**: No description
- **testVkKeyScanEx**: No description
- **testGetSystemPowerStatus**: No description
## venv\Lib\site-packages\win32\test\test_win32clipboard.py
- **TestGetSetClipboardData**: No description
- **test_data**: No description
- **test_text**: No description
## venv\Lib\site-packages\win32\test\test_win32cred.py
- **TestCredFunctions**: No description
- **test_creddelete**: No description
- **test_credgetsessiontypes**: No description
## venv\Lib\site-packages\win32\test\test_win32crypt.py
- **TestCerts**: No description
- **testSimple**: No description
- **testEntropy**: No description
- **testReadCertFiles**: No description
- **testCertBase64**: No description
- **testCertBinary**: No description
## venv\Lib\site-packages\win32\test\test_win32event.py
- **TestWaitableTimer**: No description
- **TestWaitFunctions**: No description
- **TestEvent**: No description
- **TestMutex**: No description
- **testWaitableFire**: No description
- **testCreateWaitableTimerEx**: No description
- **testWaitableTrigger**: No description
- **testWaitableError**: No description
- **testMsgWaitForMultipleObjects**: No description
- **testMsgWaitForMultipleObjects2**: No description
- **testMsgWaitForMultipleObjectsEx**: No description
- **testMsgWaitForMultipleObjectsEx2**: No description
- **testCreateEvent**: No description
- **testSetEvent**: No description
- **testResetEvent**: No description
- **testReleaseMutex**: No description
## venv\Lib\site-packages\win32\test\test_win32file.py
- **TestReadBuffer**: No description
- **TestSimpleOps**: No description
- **TestGetFileInfoByHandleEx**: No description
- **TestOverlapped**: No description
- **TestSocketExtensions**: No description
- **TestFindFiles**: No description
- **TestDirectoryChanges**: No description
- **TestEncrypt**: No description
- **TestConnect**: No description
- **TestTransmit**: No description
- **TestWSAEnumNetworkEvents**: No description
- **testLen**: No description
- **testSimpleIndex**: No description
- **testSimpleSlice**: No description
- **testSimpleFiles**: No description
- **testMoreFiles**: No description
- **testFilePointer**: No description
- **testFileTimesTimezones**: No description
- **testFileTimes**: No description
- **testFileBasicInfo**: No description
- **testSimpleOverlapped**: No description
- **testCompletionPortsMultiple**: No description
- **testCompletionPortsQueued**: No description
- **testCompletionPortsNonQueued**: No description
- **testCompletionPortsNonQueuedBadReference**: No description
- **testHashable**: No description
- **testComparable**: No description
- **testComparable2**: No description
- **testAcceptEx**: No description
- **testIter**: No description
- **testBadDir**: No description
- **testEmptySpec**: No description
- **testEmptyDir**: No description
- **testSimple**: No description
- **testSmall**: No description
- **testEncrypt**: No description
- **test_connect_with_payload**: No description
- **test_connect_without_payload**: No description
- **test_transmit**: No description
- **test_basics**: No description
- **test_functional**: No description
## venv\Lib\site-packages\win32\test\test_win32gui.py
- **TestPyGetString**: No description
- **TestPyGetMemory**: No description
- **TestEnumWindowsFamily**: No description
- **TestWindowProperties**: No description
- **test_get_string**: No description
- **test_ob**: No description
- **test_memory_index**: No description
- **test_memory_slice**: No description
- **test_real_view**: No description
- **test_memory_not_writable**: No description
- **test_enumwindows**: No description
- **test_enumchildwindows**: No description
- **test_enumdesktopwindows**: No description
- **test_classname**: No description
## venv\Lib\site-packages\win32\test\test_win32guistruct.py
- **TestBase**: No description
- **TestMenuItemInfo**: No description
- **TestMenuInfo**: No description
- **TestTreeViewItem**: No description
- **TestListViewItem**: No description
- **TestLVColumn**: No description
- **TestDEV_BROADCAST_HANDLE**: No description
- **TestDEV_BROADCAST_DEVICEINTERFACE**: No description
- **TestDEV_BROADCAST_VOLUME**: No description
- **testPackUnpack**: No description
- **testPackUnpackNone**: No description
- **testEmptyMenuItemInfo**: No description
- **testPackUnpack**: No description
- **testEmptyMenuItemInfo**: No description
- **testPackUnpack**: No description
- **testPackUnpackNone**: No description
- **testEmpty**: No description
- **testPackUnpack**: No description
- **testPackUnpackNone**: No description
- **testEmpty**: No description
- **testPackUnpack**: No description
- **testPackUnpackNone**: No description
- **testEmpty**: No description
- **testPackUnpack**: No description
- **testGUID**: No description
- **testPackUnpack**: No description
- **testPackUnpack**: No description
## venv\Lib\site-packages\win32\test\test_win32inet.py
- **TestNetwork**: No description
- **testCookies**: No description
- **testCookiesEmpty**: No description
- **testSimpleCanonicalize**: No description
- **testLongCanonicalize**: No description
- **testPythonDotOrg**: No description
- **testFtpCommand**: No description
## venv\Lib\site-packages\win32\test\test_win32net.py
- **TestCase**: No description
- **testGroupsGoodResume**: No description
- **testGroupsBadResume**: No description
## venv\Lib\site-packages\win32\test\test_win32pipe.py
- **testCallNamedPipe**: No description
- **testTransactNamedPipeBlocking**: No description
- **testTransactNamedPipeBlockingBuffer**: No description
- **testTransactNamedPipeAsync**: No description
## venv\Lib\site-packages\win32\test\test_win32print.py
- **test_printer_levels_read_dummy**: No description
## venv\Lib\site-packages\win32\test\test_win32profile.py
- **Tester**: No description
- **test_environment**: No description
## venv\Lib\site-packages\win32\test\test_win32rcparser.py
- **TestParser**: No description
- **TestGenerated**: No description
- **testStrings**: No description
- **testStandardIds**: No description
- **testTabStop**: No description
## venv\Lib\site-packages\win32\test\test_win32timezone.py
- **testWin32TZ**: No description
## venv\Lib\site-packages\win32\test\test_win32trace.py
- **TestInitOps**: No description
- **TestModuleOps**: No description
- **TestTraceObjectOps**: No description
- **TestMultipleThreadsWriting**: No description
- **TestHugeChunks**: No description
- **TestOutofProcess**: No description
- **testInitTermRead**: No description
- **testInitTermWrite**: No description
- **testTermSematics**: No description
- **testRoundTrip**: No description
- **testRoundTripUnicode**: No description
- **testBlockingRead**: No description
- **testBlockingReadUnicode**: No description
- **testFlush**: No description
- **testInit**: No description
- **testFlush**: No description
- **testIsatty**: No description
- **testRoundTrip**: No description
- **testThreads**: No description
- **testHugeChunks**: No description
- **testProcesses**: No description
## venv\Lib\site-packages\win32\test\test_win32ts.py
- **test_is_remote_session**: No description
## venv\Lib\site-packages\win32\test\test_win32wnet.py
- **TestCase**: No description
- **testGetUser**: No description
- **testNETRESOURCE**: No description
- **testWNetEnumResource**: No description
- **testNCB**: No description
- **testNetbios**: No description
- **testAddConnection**: No description
- **testAddConnectionOld**: No description
## venv\Lib\site-packages\win32com\servers\test_pycomtest.py
- No test functions found
## venv\Lib\site-packages\win32comext\bits\test\test_bits.py
- No test functions found
## venv\Lib\site-packages\win32comext\taskscheduler\test\test_addtask.py
- No test functions found
## venv\Lib\site-packages\win32comext\taskscheduler\test\test_addtask_1.py
- No test functions found
## venv\Lib\site-packages\win32comext\taskscheduler\test\test_addtask_2.py
- No test functions found
## venv\Lib\site-packages\win32comext\taskscheduler\test\test_localsystem.py
- No test functions found
