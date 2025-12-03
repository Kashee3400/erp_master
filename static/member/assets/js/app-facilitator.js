// app-facilitator.js
// Requires jQuery + DataTables to be loaded before this file.

function renderFacilitatorTable(data) {
    const $tbody = $('#facilitator-body');
    const $tfoot = $('#facilitator-footer');

    if (!Array.isArray(data) || data.length === 0) {
        $tbody.html('<tr><td colspan="8" class="text-center">No data</td></tr>');
        $tfoot.html('');
        return;
    }

    let rows = '';
    let totalInstalled = 0;

    data.forEach(item => {
        const username = item.username || '';
        const name = item.facilitator || '';
        const mcc_name = item.mcc_name || '';
        const mcc_ex_code = item.mcc_ex_code || '';
        const mpp_names = item.mpp_names || '';
        const mpp_ex_codes = item.mpp_ex_codes || '';
        const installed = Number(item.installed) ? 1 : 0;
        const pct = (typeof item.installed_percentage !== 'undefined') ? item.installed_percentage : (installed ? 100 : 0);

        totalInstalled += installed;

        rows += `<tr>
      <td>${username}</td>
      <td>${name}</td>
      <td>${mcc_name}</td>
      <td>${mcc_ex_code}</td>
      <td>${mpp_names}</td>
      <td>${mpp_ex_codes}</td>
      <td>${installed}</td>
      <td>${pct}%</td>
    </tr>`;
    });

    $tbody.html(rows);

    // Summary footer: total facilitators, installed count, installed %
    const totalFacilitators = data.length;
    const installedPct = totalFacilitators ? Math.round((totalInstalled / totalFacilitators) * 100 * 100) / 100 : 0; // 2 decimals
    const footerHtml = `
    <tr class="table-secondary fw-bold">
      <td colspan="6">Grand Total</td>
      <td>${totalInstalled}</td>
      <td>${installedPct}%</td>
    </tr>
  `;
    $tfoot.html(footerHtml);
}

function initFacilitatorDataTable() {
    const $table = $('#facilitator-table');

    if ($.fn.DataTable.isDataTable($table)) {
        return $table.DataTable();
    }

    return $table.DataTable({
        dom: 'Bfrtip',
        buttons: ['excel', 'csv'],
        responsive: true,
        pageLength: 50,
        columnDefs: [
            { targets: [2, 3, 4, 5], className: 'text-wrap' } // let hierarchy columns wrap
        ]
    });
}

function fetchFacilitatorData() {
    if (typeof facilitatorReportUrl === 'undefined') {
        console.error('facilitatorReportUrl is not defined. Make sure the template sets it before loading this JS.');
        $('#facilitator-body').html('<tr><td colspan="8" class="text-danger">Configuration error</td></tr>');
        return;
    }

    // show loading row
    $('#facilitator-body').html('<tr><td colspan="8" class="text-center">Loading...</td></tr>');
    $('#facilitator-footer').html('');

    $.ajax({
        url: facilitatorReportUrl,
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            // if DataTable already initialized, destroy prior to modifying DOM to avoid duplication
            const $table = $('#facilitator-table');
            if ($.fn.DataTable.isDataTable($table)) {
                $table.DataTable().clear().destroy();
            }

            renderFacilitatorTable(data || []);
            initFacilitatorDataTable();
        },
        error: function (xhr, status, err) {
            console.error('Failed to load facilitator data', status, err);
            $('#facilitator-body').html('<tr><td colspan="8" class="text-center text-danger">Failed to load data</td></tr>');
            $('#facilitator-footer').html('');
        }
    });
}

// automatically fetch on document ready
$(document).ready(function () {
    fetchFacilitatorData();
});
