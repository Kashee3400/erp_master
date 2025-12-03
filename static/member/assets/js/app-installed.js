// =============================================================================
// MODERN APP INSTALLATION REPORT - JAVASCRIPT
// =============================================================================

// Global state management
const AppState = {
    currentMode: 'with',
    isLoading: false,
    dataCache: {
        with: null,
        without: null
    }
};

// Utility Functions
// =============================================================================

/**
 * Show loading state with skeleton
 */
function showLoadingSkeleton(tableBodyId, colspan) {
    const skeletons = Array(5).fill(null).map(() => {
        const cells = Array(colspan).fill(null).map(() =>
            '<td><div class="loading-skeleton"></div></td>'
        ).join('');
        return `<tr>${cells}</tr>`;
    }).join('');

    $(`#${tableBodyId}`).html(skeletons);
}

/**
 * Show error message
 */
function showError(message) {
    const errorHtml = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert" style="margin: 20px;">
            <strong>Error!</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    $('.modern-card').first().prepend(errorHtml);
    setTimeout(() => $('.alert').fadeOut(), 5000);
}

/**
 * Format numbers with Indian numbering system
 */
function formatNumber(num) {
    return num?.toLocaleString('en-IN') || '0';
}

/**
 * Get percentage badge color based on value
 */
function getPercentageClass(percentage) {
    if (percentage >= 75) return 'badge-success';
    if (percentage >= 50) return 'badge-info';
    if (percentage >= 25) return 'badge-warning';
    return 'badge-warning';
}

/**
 * Create percentage badge
 */
function createPercentageBadge(percentage) {
    const badgeClass = getPercentageClass(percentage);
    return `<span class="badge-modern ${badgeClass}">${percentage}%</span>`;
}

/**
 * Safe value getter with fallback
 */
function safeValue(value, fallback = 'N/A') {
    return value !== null && value !== undefined && value !== '' ? value : fallback;
}

/**
 * Destroy DataTable if exists
 */
function destroyDataTable(tableSelector) {
    const table = $(tableSelector);
    if ($.fn.DataTable.isDataTable(table)) {
        table.DataTable().destroy();
    }
}

/**
 * Initialize DataTable with modern config
 */
function initializeDataTable(tableSelector, config = {}) {
    destroyDataTable(tableSelector);

    const defaultConfig = {
        dom: "Bfrtip",
        buttons: [
            {
                extend: 'excel',
                text: '📊 Export Excel',
                className: 'dt-button'
            },
            {
                extend: 'csv',
                text: '📄 Export CSV',
                className: 'dt-button'
            },
            {
                extend: 'print',
                text: '🖨️ Print',
                className: 'dt-button'
            }
        ],
        pageLength: 50,
        responsive: true,
        language: {
            search: "🔍 Search:",
            lengthMenu: "Show _MENU_ entries",
            info: "Showing _START_ to _END_ of _TOTAL_ entries",
            emptyTable: "No data available",
            zeroRecords: "No matching records found"
        },
        order: [[0, 'asc']],
        ...config
    };

    return $(tableSelector).DataTable(defaultConfig);
}

// Data Processing Functions
// =============================================================================

/**
 * Update statistics cards
 */
function updateStatsCards(data) {
    if (!data || data.length === 0) return;

    const totalRow = data.find(item => item.is_total);
    if (!totalRow) return;

    $('#stat-total-members').text(formatNumber(totalRow.total_members || 0));
    $('#stat-installed').text(formatNumber(totalRow.installed || 0));
    $('#stat-pourers').text(formatNumber(totalRow.pourers || 0));
    $('#stat-percentage').text(`${totalRow.installed_percentage || 0}%`);
}

/**
 * Build table row for WITHOUT collection mode
 */
function buildWithoutCollectionRow(item) {
    if (item.is_total) {
        return `
            <tr class="table-secondary fw-bold" style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);">
                <td colspan="5" style="text-align: right; padding-right: 20px;">
                    <strong>📊 Grand Total</strong>
                </td>
                <td><strong>${formatNumber(item.total_members || 0)}</strong></td>
                <td><strong>${formatNumber(item.installed || 0)}</strong></td>
                <td><strong>${createPercentageBadge(item.installed_percentage || 0)}</strong></td>
            </tr>
        `;
    }

    return `
        <tr>
            <td>${safeValue(item.mcc?.name)}</td>
            <td>${safeValue(item.mcc?.mcc_ex_code)}</td>
            <td>${safeValue(item.mpp?.name)}</td>
            <td>${safeValue(item.mpp?.mpp_ex_code)}</td>
            <td>${safeValue(item.fs_name)}</td>
            <td>${formatNumber(item.total_members || 0)}</td>
            <td>${formatNumber(item.installed || 0)}</td>
            <td>${createPercentageBadge(item.installed_percentage || 0)}</td>
        </tr>
    `;
}

/**
 * Build table row for WITH collection mode
 */
function buildWithCollectionRow(item) {
    if (item.is_total) {
        return `
            <tr class="table-secondary fw-bold" style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);">
                <td colspan="5" style="text-align: right; padding-right: 20px;">
                    <strong>📊 Grand Total</strong>
                </td>
                <td><strong>${formatNumber(item.total_members || 0)}</strong></td>
                <td><strong>${formatNumber(item.pourers || 0)}</strong></td>
                <td><strong>${formatNumber(item.installed || 0)}</strong></td>
                <td><strong>${createPercentageBadge(item.installed_percentage || 0)}</strong></td>
            </tr>
        `;
    }

    return `
        <tr>
            <td>${safeValue(item.mcc?.name)}</td>
            <td>${safeValue(item.mcc?.mcc_ex_code)}</td>
            <td>${safeValue(item.mpp?.name)}</td>
            <td>${safeValue(item.mpp?.mpp_ex_code)}</td>
            <td>${safeValue(item.fs_name)}</td>
            <td>${formatNumber(item.total_members || 0)}</td>
            <td>${formatNumber(item.pourers || 0)}</td>
            <td>${formatNumber(item.installed || 0)}</td>
            <td>${createPercentageBadge(item.installed_percentage || 0)}</td>
        </tr>
    `;
}

// API Functions
// =============================================================================

/**
 * Fetch WITHOUT collection data
 */
function fetchWithoutCollection() {
    if (AppState.isLoading) return;

    AppState.isLoading = true;
    const $table = $('#mcc-table-without');
    const url = `${mccReportUrl}?mode=without`;

    showLoadingSkeleton('without-body', 8);

    $.ajax({
        url: url,
        type: "GET",
        timeout: 30000,
        success: function (data) {
            if (!data || data.length === 0) {
                $('#without-body').html('<tr><td colspan="8" class="text-center">No data available</td></tr>');
                $('#without-footer').html('');
                return;
            }

            AppState.dataCache.without = data;

            let rows = "";
            let totalRow = "";

            data.forEach(item => {
                if (item.is_total) {
                    totalRow = buildWithoutCollectionRow(item);
                } else {
                    rows += buildWithoutCollectionRow(item);
                }
            });

            $('#without-body').html(rows);
            $('#without-footer').html(totalRow);

            initializeDataTable($table);
        },
        error: function (xhr, status, error) {
            console.error('Error fetching without collection data:', error);
            $('#without-body').html(`
                <tr>
                    <td colspan="8" class="text-center text-danger">
                        ⚠️ Error loading data. Please try again.
                    </td>
                </tr>
            `);
            showError('Failed to load data. Please check your connection and try again.');
        },
        complete: function () {
            AppState.isLoading = false;
        }
    });
}

/**
 * Fetch WITH collection data
 */
function fetchWithCollection() {
    if (AppState.isLoading) return;

    AppState.isLoading = true;
    const $table = $('#mcc-table-with');
    const fromDate = $('#from-date').val();
    const toDate = $('#to-date').val();

    // Validate dates
    if (!fromDate || !toDate) {
        showError('Please select both From Date and To Date');
        AppState.isLoading = false;
        return;
    }

    if (new Date(fromDate) > new Date(toDate)) {
        showError('From Date cannot be after To Date');
        AppState.isLoading = false;
        return;
    }

    let url = `${mccReportUrl}?mode=with&from=${fromDate}&to=${toDate}`;

    showLoadingSkeleton('with-body', 9);
    $('#stats-section').fadeOut(200);

    $.ajax({
        url: url,
        type: "GET",
        timeout: 30000,
        success: function (data) {
            if (!data || data.length === 0) {
                $('#with-body').html('<tr><td colspan="9" class="text-center">No data available</td></tr>');
                $('#with-footer').html('');
                return;
            }

            AppState.dataCache.with = data;

            let rows = "";
            let totalRow = "";

            data.forEach(item => {
                if (item.is_total) {
                    totalRow = buildWithCollectionRow(item);
                } else {
                    rows += buildWithCollectionRow(item);
                }
            });

            $('#with-body').html(rows);
            $('#with-footer').html(totalRow);

            // Update stats cards
            updateStatsCards(data);
            $('#stats-section').fadeIn(300);

            initializeDataTable($table);
        },
        error: function (xhr, status, error) {
            console.error('Error fetching with collection data:', error);
            $('#with-body').html(`
                <tr>
                    <td colspan="9" class="text-center text-danger">
                        ⚠️ Error loading data. Please try again.
                    </td>
                </tr>
            `);

            if (xhr.status === 400) {
                showError(xhr.responseJSON?.error || 'Invalid request. Please check your date range.');
            } else {
                showError('Failed to load data. Please check your connection and try again.');
            }
        },
        complete: function () {
            AppState.isLoading = false;
        }
    });
}

/**
 * Fetch Sahayak data
 */
function fetchAndSahayakRenderData() {
    if (typeof sahayakReportUrl === 'undefined') {
        console.warn('Sahayak report URL not defined');
        return;
    }

    const $table = $('#sahayak-data-table');

    $.ajax({
        url: sahayakReportUrl,
        type: "GET",
        timeout: 30000,
        beforeSend: function () {
            showLoadingSkeleton('sahayak-table-body', 6);
        },
        success: function (data) {
            if (!data || data.length === 0) {
                $('#sahayak-table-body').html('<tr><td colspan="6" class="text-center">No data available</td></tr>');
                $('#sahayak-data-footer').html('');
                return;
            }

            let rows = "";
            let totalRow = "";

            data.forEach(item => {
                if (item.is_total) {
                    totalRow = `
                        <tr class="table-secondary fw-bold" style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);">
                            <td colspan="5" style="text-align: right; padding-right: 20px;">
                                <strong>📊 Grand Total</strong>
                            </td>
                            <td><strong>${formatNumber(item.installed || 0)}</strong></td>
                        </tr>
                    `;
                } else {
                    rows += `
                        <tr>
                            <td>${safeValue(item.mcc_name)}</td>
                            <td>${safeValue(item.mcc_ex_code)}</td>
                            <td>${safeValue(item.mpp_name)}</td>
                            <td>${safeValue(item.mpp_ex_code)}</td>
                            <td>${safeValue(item.fs_name)}</td>
                            <td>${formatNumber(item.installed || 0)}</td>
                        </tr>
                    `;
                }
            });

            $('#sahayak-table-body').html(rows);
            $('#sahayak-data-footer').html(totalRow);

            initializeDataTable($table);
        },
        error: function (xhr, status, error) {
            console.error('Error fetching sahayak data:', error);
            $('#sahayak-table-body').html(`
                <tr>
                    <td colspan="6" class="text-center text-danger">
                        ⚠️ Error loading data. Please try again.
                    </td>
                </tr>
            `);
        }
    });
}

// Event Handlers
// =============================================================================

/**
 * Toggle between WITH and WITHOUT collection modes
 */
$('#toggle-collection').on('change', function () {
    const isChecked = $(this).is(':checked');
    AppState.currentMode = isChecked ? 'with' : 'without';

    if (isChecked) {
        // Switch to WITH collection mode
        $("#without-collection-section").fadeOut(200, function () {
            $("#with-collection-section").fadeIn(300);
            $("#stats-section").fadeIn(300);
        });
        fetchWithCollection();
    } else {
        // Switch to WITHOUT collection mode
        $("#with-collection-section").fadeOut(200, function () {
            $("#without-collection-section").fadeIn(300);
        });
        $("#stats-section").fadeOut(200);
        fetchWithoutCollection();
    }
});

/**
 * Apply date range filters (only affects WITH collection mode)
 */
$('#apply-filters').on('click', function () {
    if ($('#toggle-collection').is(':checked')) {
        fetchWithCollection();
    }
});

/**
 * Allow Enter key to trigger filter application
 */
$('#from-date, #to-date').on('keypress', function (e) {
    if (e.which === 13) { // Enter key
        $('#apply-filters').click();
    }
});

// Initialization
// =============================================================================

$(document).ready(function () {

    // Set default dates (last 30 days)
    const today = new Date();
    const thirtyDaysAgo = new Date(today.getTime() - (30 * 24 * 60 * 60 * 1000));

    $('#to-date').val(today.toISOString().split('T')[0]);
    $('#from-date').val(thirtyDaysAgo.toISOString().split('T')[0]);

    // Default: collection ON
    $('#toggle-collection').prop('checked', true);
    AppState.currentMode = 'with';

    // Show WITH section, hide WITHOUT section
    $("#without-collection-section").hide();
    $("#with-collection-section").show();

    // Initial data fetch
    fetchWithCollection();
    fetchAndSahayakRenderData();

    // Add keyboard shortcut: Ctrl/Cmd + R to refresh
    $(document).on('keydown', function (e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            if (AppState.currentMode === 'with') {
                fetchWithCollection();
            } else {
                fetchWithoutCollection();
            }
            fetchAndSahayakRenderData();
        }
    });

    console.log('✅ App Installation Report initialized successfully');
});