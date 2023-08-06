
TASK_DEFAULT_ATTRIBUTES = dict(
    template_type='TASK',
    entity_ids=[],
    resource_ids=[],
    file_ids=[],
    worker_ids=[],
    document_ids=[],
    skill_ids=[],
    enable_time_window_display=False,
    unscheduled=False,
    is_linked=False,
    task_without_time=False,
    is_locked=False,
    is_booking=False,
    enable_expected_date_range=False,
)

ROUTE_DEFAULT_ATTRIBUTES = dict(
    entity_ids=[],
    resource_ids=[],
    start_and_end_at_depot=False,
    is_published_once=False,
    padding_between_tasks=0,
)

TASK_ATTRIBUTES_TO_EXCLUDE_IN_VALIDATION = [
    'owner', 'status', 'status_id', 'status_title', 'notifications', 'notifications_sent', 'series',
    'pending_review_reminder_time', 'pending_review_reminder_attempts_left',
    'queued_task_name', 'is_archived', 'created', 'updated', 'routes', 'mileage',
    'travel_time', 'task_time', 'total_time', 'do_not_send_webhook_notification', 'entity_confirmation_statuses',
    'structured_entity_confirmation_statuses', 'task_final_confirmation_status', 'series_id', 'id', 'parent_task_external_id',
]

TASK_ATTRIBUTES = ['created_by', 'source', 'source_id', 'template', 'template_type', 'title', 'details',
                   'start_datetime', 'start_datetime_original_iso_str', 'start_datetime_timezone', 'end_datetime',
                   'end_datetime_original_iso_str', 'end_datetime_timezone', 'extra_fields', 'entity_ids', 'resource_ids',
                   'customer_first_name', 'customer_last_name', 'customer_email', 'customer_company_name',
                   'customer_address_line_1', 'customer_address_line_2', 'customer_address', 'customer_city',
                   'customer_state', 'customer_country', 'customer_zipcode', 'customer_exact_location',
                   'customer_phone', 'customer_mobile_number', 'customer_id', 'customer_notes', 'customer_timezone',
                   'enable_time_window_display', 'time_window_start', 'use_assignee_color', 'file_ids', 'unscheduled',
                   'external_id', 'external_url', 'additional_addresses', 'current_destination', 'group_id', 'items',
                   'route_id', 'internal_route_id', 'duration', 'worker_ids', 'all_day', 'number_of_workers_required',
                   'company_id', 'template_extra_fields', 'document_ids', 'external_type', 'is_supply_provided_locked',
                   'is_supply_returned_locked', 'is_linked', 'forms', 'linked_internal_ref', 'linked_external_ref',
                   'customer_type', 'is_customer_address_geo_coded', 'use_lat_lng_address', 'skill_ids', 'task_without_time',
                   'is_locked', 'is_booking', 'booking_id', 'booking_slot_id', 'additional_info', 'external_resource_type',
                   'enable_expected_date_range', 'expected_start_datetime', 'expected_start_datetime_original_iso_str',
                   'expected_end_datetime', 'expected_end_datetime_original_iso_str', 'external_live_track_link',
                   'additional_contacts', 'recurring_tasks_settings_id', 'recurring_tasks_settings_title', 'created_by_user',
                   'updated_by_user', 'updated_by', 'position_in_route', 'owner', 'status', 'status_id', 'status_title',
                   'notifications', 'notifications_sent', 'series', 'pending_review_reminder_time', 'pending_review_reminder_attempts_left',
                   'queued_task_name', 'is_archived', 'routes', 'mileage', 'travel_time', 'task_time', 'total_time',
                   'do_not_send_webhook_notification', 'entity_confirmation_statuses', 'structured_entity_confirmation_statuses',
                   'task_final_confirmation_status', 'id', 'series_id', 'parent_task_external_id', 'due_datetime',
                   'due_datetime_original_iso_str', 'self_scheduling', 'is_without_datetime', 'basic_schedule', 'is_multi_day', 'activity_type',
                   'is_route_activity', 'checklists', 'checklist_items', 'external_integration_info', 'customer_name']


ROUTE_ATTRIBUTES = ['owner', 'created_by', 'start_datetime', 'start_datetime_original_iso_str', 'end_datetime',
                    'end_datetime_original_iso_str', 'title', 'description', 'extra_fields', 'entity_ids', 'resource_ids', 'external_id',
                    'is_disabled', 'total_tasks', 'status', 'type', 'padding_between_tasks', 'start_and_end_at_depot', 'depot_addresses',
                    'is_published_once', 'group_id', 'color']


ATTRIBUTES_THAT_CAN_BE_UPDATED_IN_ROUTE_DRAFT = ['title', 'start_datetime', 'start_datetime_original_iso_str',
                                                 'end_datetime', 'end_datetime_original_iso_str', 'entity_ids',
                                                 'total_tasks', 'start_and_end_at_depot', 'depot_addresses',
                                                 'padding_between_tasks', 'resource_ids']

ATTRIBUTES_REQUIRED_TO_CREATE_NEW_ROUTE_DRAFT = ['title', 'start_datetime', 'start_datetime_original_iso_str',
                                                 'end_datetime', 'end_datetime_original_iso_str', 'entity_ids',
                                                 'total_tasks', 'start_and_end_at_depot', 'depot_addresses',
                                                 'padding_between_tasks', 'is_published_once']


# any change in below list should also be made in route.js file in front-end's helpers directory
ATTRIBUTES_THAT_CAN_BE_UPDATED_IN_TASK_DRAFT = ['start_datetime', 'start_datetime_original_iso_str',
                                                'start_datetime_timezone', 'end_datetime',
                                                'end_datetime_original_iso_str', 'end_datetime_timezone', 'duration',
                                                'entity_ids', 'resource_ids', 'unscheduled',
                                                'enable_time_window_display', 'time_window_start', 'is_locked', 'task_without_time',
                                                'position_in_route']
# Assumption:
# start_datetime attr will always come first and then end_datetime.
# any change in below list should consider this order.
ATTRIBUTES_REQUIRED_TO_CREATE_NEW_TASK_DRAFT = ['start_datetime', 'start_datetime_original_iso_str',
                                                'start_datetime_timezone', 'end_datetime',
                                                'end_datetime_original_iso_str', 'end_datetime_timezone', 'duration',
                                                'entity_ids', 'resource_ids', 'unscheduled',
                                                'internal_route_id', 'enable_time_window_display',
                                                'time_window_start', 'is_locked', 'task_without_time',
                                                'additional_route_ids']

TASK_DRAFT_ATTRIBUTES_WHICH_INDICATES_WARNING_ON_UI = ['start_datetime', 'end_datetime', 'duration', 'entity_ids',
                                                       'resource_ids', 'enable_time_window_display', 'time_window_start',
                                                       'task_without_time']
