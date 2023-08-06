
CHANGELOG
=========

0.8.238 (2022-08-03)
--------------------

* Improve "touch" logic for employees.

* Stop using the old ``rattail.db.api.settings`` module.

* Force cache invalidation when Raw Setting is edited.


0.8.237 (2022-07-27)
--------------------

* Add some more views to potentially include via poser.

* Misc. improvements for desktop receiving views.


0.8.236 (2022-07-25)
--------------------

* Add setting to expose/hide "active in POS" customer flag.

* Allow optional row grid title for master view.

* Add basic/minimal merge support for customers.

* Assume default vendor for new receiving batch.

* Add basic edit support for Purchases.

* Add ``iter(Form)`` logic, to loop through fields.

* Add "auto-receive all items" support for receiving batch API.


0.8.235 (2022-07-22)
--------------------

* Split out rendering of ``this-page`` component in falafel theme.

* Allow download of results for common product-related tables.

* Make caching products optional, when creating vendor catalog batch.

* Expose the ``complete`` flag for pricing batch.

* Add ``template_kwargs_clone()`` stub for master view.

* Misc deform template improvements.


0.8.234 (2022-07-18)
--------------------

* Fix form validation for app settings page w/ buefy theme.

* Honor default pagesize for all grids, per setting.

* Add basic "download results" for Subdepartments grid.

* Add new-style config defaults for BrandView.


0.8.233 (2022-06-24)
--------------------

* Add minimal buefy support for 'percentinput' field widget.

* Add autocomplete support for subdepartments.


0.8.232 (2022-06-14)
--------------------

* Let default grid page size correspond to first option.

* Add start date support for "future" pricing batch.


0.8.231 (2022-05-15)
--------------------

* Expose config for identifying supported vendors.

* Allow restricting to supported vendors only, for Receiving.


0.8.230 (2022-05-10)
--------------------

* Sort roles list when viewing a user.

* Add grid workarounds when data is list instead of query.


0.8.229 (2022-05-03)
--------------------

* Tweak how family data is displayed.


0.8.228 (2022-04-13)
--------------------

* Fix quotes for field helptext.

* Flush early when populating batch, to ensure error is shown.


0.8.227 (2022-04-04)
--------------------

* Add touch for report codes.

* Raise 404 if report not found.

* Add template kwargs stub for ``view_row()``.

* Log error when failing to submit new custorder batch.

* Honor case vs. unit restrictions for new custorder.

* Tweak where description field is shown for receiving batch.

* Fix "touch" url for non-standard record types.


0.8.226 (2022-03-29)
--------------------

* Let errors raise when showing poser reports.


0.8.225 (2022-03-29)
--------------------

* Force session flush within try/catch, for batch refresh.


0.8.224 (2022-03-25)
--------------------

* Improve vendor validation for new receiving batch.

* Use common logic for fetching batch handler.


0.8.223 (2022-03-21)
--------------------

* Show link to txn as field when viewing trainwreck item.


0.8.222 (2022-03-17)
--------------------

* Expose custorder xref markers for trainwreck.


0.8.221 (2022-03-16)
--------------------

* Always show batch params by default when viewing.

* Show helptext when applicable for "new batch from product query".

* Make problem report titles searchable in grid.


0.8.220 (2022-03-15)
--------------------

* Log error instead of warning, when batch population fails.

* Add default help link for Receiving feature.


0.8.219 (2022-03-10)
--------------------

* Cleanup grid filters for vendor catalog batches.

* Cleanup view config syntax for vendor catalog batch.

* Add workaround when inserting new fields to form field list.

* Add ``Form.insert()`` method, to insert field based on index.

* Default behavior for report chooser should *not* be form/dropdown.


0.8.218 (2022-03-08)
--------------------

* Log warning/traceback when failing to include a configured view.

* Fix gotcha when defining new provider views.

* Bump the default Buefy version to 0.8.13.


0.8.217 (2022-03-07)
--------------------

* Add the "provider" concept, let them configure db sessions.

* Let providers add extra views, options for includes config.

* Let tailbone providers include static views.

* Link to email settings profile when viewing email attempt.


0.8.216 (2022-03-05)
--------------------

* Show list of generated reports when viewing Poser Report.

* Show link back to Poser Report when viewing Generated Report.

* Always include ``app_title`` in global template rendering context.

* Update some more view config syntax.

* Make common web view a bit more common.

* Improve the Poser Setup page; allow poser dir refresh.

* Add initial/basic support for configuring "included views".

* Add ``tailbone.views.essentials`` to include common / "core" views.

* Add flash message when upgrade execution completes (pass or fail).


0.8.215 (2022-03-02)
--------------------

* Show toast msg instead of alert after sending feedback.

* Add basic support for Poser reports, list/create.


0.8.214 (2022-03-01)
--------------------

* Params should be readonly when editing batch.

* Tweak styles for links in object helper panel.


0.8.213 (2022-03-01)
--------------------

* Add simple searchable column support for non-AJAX grids.

* Fix stdout/stderr fields for upgrade view.

* Pass query along for download results, so subclass can modify.

* Avoid making discounts data if missing field, for trainwreck item view.


0.8.212 (2022-02-26)
--------------------

* Add page/way to configure main menus.


0.8.211 (2022-02-25)
--------------------

* Add view template stub for trainwreck transaction.

* Add auto-filter hyperlinks for batch row status breakdown.

* Auto-filter hyperlinks for PO vs. invoice breakdown in Receiving.

* Add grid hyperlinks for trainwreck transaction line items.

* Use dict instead of custom object to represent menus.

* Expose "discount type" for Trainwreck line items.


0.8.210 (2022-02-20)
--------------------

* Only show DB picker for permissioned users.

* Expose some new trainwreck fields; per-item discounts.

* Show SRP as currency for vendor catalog batch.


0.8.209 (2022-02-16)
--------------------

* Fix progress bar when running problem report.


0.8.208 (2022-02-15)
--------------------

* Allow override of navbar-end element in falafel theme header.

* Add initial support for editing user preferences.

* Add FormPosterMixin to WholePage class.


0.8.207 (2022-02-13)
--------------------

* Try out new config defaults function for some views (user, customer).

* Add highlight for non-active users, customers in grid.

* Prevent cache for index pages by default, unless configured not to.

* Cleanup labels for Vendor/Code "preferred" vs. "any" in products grid.

* Add config for showing ordered vs. shipped amounts when receiving.

* Tweak how "duration" fields are rendered for grids, forms.

* New upgrades should be enabled by default.


0.8.206 (2022-02-08)
--------------------

* Add "full lookup" product search modal for new custorder page.


0.8.205 (2022-02-05)
--------------------

* Tweak how product key field is handled for product views.

* Add some autocomplete workarounds for new vendor catalog batch.


0.8.204 (2022-02-04)
--------------------

* Add ``CustomerGroupAssignment`` to customer version history.


0.8.203 (2022-02-01)
--------------------

* Expose batch params for vendor catalogs.


0.8.202 (2022-01-31)
--------------------

* Make "generate report" the same as "create new generated report".


0.8.201 (2022-01-31)
--------------------

* Show helptext for params when generating new report.

* Tweak handling of empty params when generating report.


0.8.200 (2022-01-31)
--------------------

* Improve profile link helper for buefy themes.

* Add project generator support for rattail-integration, tailbone-integration.


0.8.199 (2022-01-26)
--------------------

* Tweak the "auto-receive all" tool for Chrome browser.


0.8.198 (2022-01-25)
--------------------

* Only expose "product" departments within product view dropdowns.


0.8.197 (2022-01-19)
--------------------

* Use buefy input for quickie search.


0.8.196 (2022-01-15)
--------------------

* Use the new label handler.


0.8.195 (2022-01-13)
--------------------

* Strip whitespace for new customer fields, in new custorder page.


0.8.194 (2022-01-12)
--------------------

* Include all static files in manifest.

* Update usage of ``app.get_email_handler()`` to avoid warnings.


0.8.193 (2022-01-10)
--------------------

* Add buefy support for quick-printing product labels; also speed bump.

* Add way to set form-wide schema validator.

* Add progress support when deleting a batch.

* Expose the Sale, TPR, Current price fields for label batch.


0.8.192 (2022-01-08)
--------------------

* Add configurable template file for vendor catalog batch.

* Some aesthetic improvements for vendor catalog batch.

* Several disparate changes needed for vendor catalog improvements.

* Expose, honor "allow future" setting for vendor catalog batch.

* Add config for supported vendor catalog parsers.

* Update some method calls to avoid deprecation warnings.


0.8.191 (2022-01-03)
--------------------

* Fix permission check for input file template links.

* Remove usage of ``app.get_designated_import_handler()``.

* Add basic configure page for Trainwreck.

* Use ``AuthHandler.get_permissions()``.


0.8.190 (2021-12-29)
--------------------

* Show create button on "most" pages for a master view.

* Expose products setting for type 2 UPC lookup.

* Add basic "resolve" support for person, product from new custorder.


0.8.189 (2021-12-23)
--------------------

* Add basic "pending product" support for new custorder batch.

* Improve email bounce view per buefy theme.


0.8.188 (2021-12-20)
--------------------

* Flag discontinued items for main Products grid.


0.8.187 (2021-12-20)
--------------------

* Add common configuration logic for "input file templates".

* Add some standard CRUD buttons for buefy themes.


0.8.186 (2021-12-17)
--------------------

* Render "pretty" UPC by default, for batch row form fields.

* Let config decide which versions of vue.js and buefy to use.


0.8.185 (2021-12-15)
--------------------

* Allow for null price when showing price history.

* Overhaul desktop views for receiving, for efficiency.

* Add some basic "config" views, to obviate some App Settings.

* Add "jump to" chooser in App Settings, for various "configure" pages.

* Fix params field when deleting a report.

* Add some smarts when making batch execution form schema.


0.8.184 (2021-12-09)
--------------------

* Refactor "receive row" and "declare credit" tools per buefy theme.

* Allow "auto-receive all items" batch feature in production.

* Make "view row" prettier for receiving batch, for buefy themes.

* Add buttons to edit, confirm cost for receiving batch row view.


0.8.183 (2021-12-08)
--------------------

* Add basic views to expose Problem Reports, and run them.

* Only include ``--runas`` arg if we have a value, for import jobs.

* Assume default receiving workflow if there is only one.

* Fix bug when report has no params dict.


0.8.182 (2021-12-07)
--------------------

* Fix form ref bug, for batch execution.


0.8.181 (2021-12-07)
--------------------

* Bugfix.


0.8.180 (2021-12-07)
--------------------

* Add basic import/export handler views, tool to run jobs.

* Overhaul import handler config etc.:
  * add ``MasterView.configurable`` concept, ``/configure.mako`` template
  * add new master view for DataSync Threads (needs content)
  * tweak view config for DataSync Changes accordingly
  * update the Configure DataSync page per ``configurable`` concept
  * add new Configure Import/Export page, per ``configurable``
  * add basic views for Raw Permissions

* Honor "safe for web app" flags for import/export handlers.

* When viewing report output, show params as proper buefy table.


0.8.179 (2021-12-03)
--------------------

* Expose the Sale Price and TPR Price for product views.


0.8.178 (2021-11-29)
--------------------

* Add page for configuring datasync.


0.8.177 (2021-11-28)
--------------------

* Show current/sale pricing for products in new custorder page.

* Add simple search filters for past items dialog in new custorder.


0.8.176 (2021-11-25)
--------------------

* Add basic support for receiving from PO with invoice.

* Don't use multi-select for new report in buefy themes.


0.8.175 (2021-11-17)
--------------------

* Fix bug when product has empty suggested price.

* Show ordered quantity when viewing costing batch row.


0.8.174 (2021-11-14)
--------------------

* Expose the "sync users" flag for Roles.


0.8.173 (2021-11-11)
--------------------

* Improve error handling when executing a custorder batch.

* Fix "download results" support for Products.


0.8.172 (2021-11-11)
--------------------

* Add permission for viewing "all" employees.


0.8.171 (2021-11-11)
--------------------

* Add "true margin" to products XLSX export.

* Add initial ``VersionMasterView`` base class.

* Add views for ``PendingProduct`` model; also ``DepartmentWidget``.


0.8.170 (2021-11-09)
--------------------

* Fix dynamic content title for "view profile" page.


0.8.169 (2021-11-08)
--------------------

* Use products handler to get image URL.

* Show some more product attributes in custorder item selection popup.

* Auto-select Quantity tab when editing item for new custorder.

* Let user "add past product" when making new custorder.

* Let handler restrict available invoice parser options.

* Cleanup grid columns for receiving batches.

* Fall back to empty string for product regular price.


0.8.168 (2021-11-05)
--------------------

* Make separate method for writing results XLSX file.

* Add ``render_brand()`` method for MasterView.

* Add link to download generic template for vendor catalog batch.


0.8.167 (2021-11-04)
--------------------

* Try to prevent caching for any /index (grid) page.

* Fix product view page when user cannot view version history.

* Move some custorder logic to handler; allow force-swap of product selection.

* Honor the "product price may be questionable" flag for new custorder.

* Show unit price in line items grid for new custorder.

* Avoid exposing batch params when creating a batch.


0.8.166 (2021-11-03)
--------------------

* Fix the Department filter for Products grid, for jquery themes.


0.8.165 (2021-11-02)
--------------------

* Optionally set the ``sticky-header`` attribute for main buefy grids.

* Show case qty by default for costing batch rows.

* Highlight the "did not receive" rows for purchase batch.

* Improve validation for Person field of User form.

* Omit "edit" link unless user has perm, for Customer "people" subgrid.

* Highlight "cannot calculate price" rows for new product batch.


0.8.164 (2021-10-20)
--------------------

* Give custorder batch handler a couple ways to affect adding new items.

* Refactor to leverage all existing methods of auth handler.

* Overhaul the autocomplete component, for sake of new custorder.

* Improve "refresh contact", show new fields in green for custorder.

* Invoke handler when adding new item to custorder batch.

* Add basic "price needs confirmation" support for custorder.

* Clean up the product selection UI for new custorder.


0.8.163 (2021-10-14)
--------------------

* Misc. tweaks for users, roles.


0.8.162 (2021-10-14)
--------------------

* Cleanup form display a bit, for App Settings.

* Invoke the auth handler to cache user permissions etc.


0.8.161 (2021-10-13)
--------------------

* Add ``debounce()`` wrapper for buefy autocomplete.

* Leverage the auth handler for main user login.


0.8.160 (2021-10-11)
--------------------

* Stop rounding case/unit cost fields to 2 places for purchase batch.

* Fix some phone/email bugs for new custorder page.

* Fix bug when making context for mailing address.

* Improve display, handling for "add contact info to customer record".


0.8.159 (2021-10-10)
--------------------

* Simplify template context customization for view_profile_buefy.


0.8.158 (2021-10-07)
--------------------

* Add support for "new customer" when creating new custorder.

* Improve contact name handling for new custorder.


0.8.157 (2021-10-06)
--------------------

* Some tweaks for invoice costing batch views.

* Add "restrict contact info" features for new custorder batch.

* Add "contact update request" workflow for new custorder batch.


0.8.156 (2021-10-05)
--------------------

* Show "contact notes" when creating new custorder.

* Improve phone editing for new custorder.

* Add button to refresh contact info for new custorder.

* Overhaul the "Personal" tab of profile view.

* Refactor the Employee tab of profile view, per better patterns.


0.8.155 (2021-10-01)
--------------------

* Refactor autocomplete view logic to leverage new "autocompleters".


0.8.154 (2021-09-30)
--------------------

* Initial (basic) views for invoice costing batches.


0.8.153 (2021-09-28)
--------------------

* Improve phone/email handling when making new custorder.

* Avoid "detach person" logic if not supported by view class.


0.8.152 (2021-09-27)
--------------------

* Allow changing status, adding notes for customer order items.


0.8.151 (2021-09-27)
--------------------

* Overhaul new custorder so contact may be either Person or Customer.

* Add a dropdown of choices to the Department filter for Products grid.


0.8.150 (2021-09-26)
--------------------

* Refactor several "field grids" per Buefy theme.

* Display the Store field for Customer Orders.


0.8.149 (2021-09-25)
--------------------

* Improve default autocomplete query logic, w/ multiple ILIKE.

* Add placeholder to customer lookup for new order.

* Invoke handler for customer autocomplete when making new custorder.

* Improve "employees" list when viewing a department, for buefy themes.

* Add products row grid for misc. org table views.


0.8.148 (2021-09-22)
--------------------

* Add way to update Employee ID from profile view.


0.8.147 (2021-09-22)
--------------------

* Add way to override grid action label rendering.


0.8.146 (2021-09-21)
--------------------

* Misc. improvements for customer order views.


0.8.145 (2021-09-19)
--------------------

* Allow setting the "exclusive" sequence of grid filters.


0.8.144 (2021-09-16)
--------------------

* Invoke handler when request is made to merge 2 people.


0.8.143 (2021-09-12)
--------------------

* Add way to customize product autocomplete for new custorder.


0.8.142 (2021-09-09)
--------------------

* Set quantity type when viewing vendor lead times, order intervals.


0.8.141 (2021-09-09)
--------------------

* Add /people API endpoint; allow for "native sort".

* Allow override of "create" permission in API.

* Add the ``Grid.remove()`` method, deprecate ``hide_column()`` etc.

* Improve error handling for purchase batch.


0.8.140 (2021-09-01)
--------------------

* Make it easier to override rendering grid component in master/index.

* Always show all grid actions...for now.

* Allow grid columns to be *invisible* (but still present in grid).

* Improve UI, customization hooks for new custorder batch.

* Add hover text for vendor ID column of pricing batch row grid.

* Fix size of roles multi-select when editing user.

* Allow "touch" action for employees.


0.8.139 (2021-08-26)
--------------------

* Tweak how email preview is sent, and attempt "to" is displayed.

* Move "merge 2 people" logic into People Handler.

* Expose "merge request tracking" feature for People data.

* Allow customization of row 'view' action url.

* Require explicit opt-in for "clicking grid row checks box" feature.

* Add ``before_render_index()`` customization hook for MasterView.


0.8.138 (2021-08-04)
--------------------

* Let feedback forms define their own email key.


0.8.137 (2021-07-15)
--------------------

* Set UPC renderer for delproduct batch row.

* Expose ``pack_size`` for delproduct batch.


0.8.136 (2021-06-18)
--------------------

* Include "is/not null" filters for GPC fields.


0.8.135 (2021-06-15)
--------------------

* Add 'v' prefix for release package diff links.


0.8.134 (2021-06-15)
--------------------

* Allow config to set favicon and header image.


0.8.133 (2021-06-11)
--------------------

* Allow customization of rendering version diff values.

* Allow direct creation of new label batches.

* Allow generating project which integrates w/ LOC SMS.


0.8.132 (2021-05-03)
--------------------

* Highlight "has inventory" rows for delete item batch.

* Add csrftoken to TailboneForm js.

* Freeze pyramid version at 1.x.


0.8.131 (2021-04-12)
--------------------

* Show current price date range as hover text, for products grid.

* Make it easier to extend "common" API views.

* Accept any decimal numbers for API inventory batch counts.


0.8.130 (2021-03-30)
--------------------

* Catch and show error, if one happens when making batch from product query.

* Expose the new ``Store.archived`` flag.


0.8.129 (2021-03-11)
--------------------

* Add support for ``inactivity_months`` field for delete product batch.

* Expose new fields for Trainwreck.

* Fix enum display for customer order status.


0.8.128 (2021-03-05)
--------------------

* Allow per-user stylesheet for Buefy themes.

* Expose ``date_created`` for delete product batches.


0.8.127 (2021-03-02)
--------------------

* Use end time as default filter, sort for Trainwreck.

* Avoid encoding values as string, for integer grid filters.

* Fix message recipients for Reply / Reply-All, with Buefy themes.

* Handle row click as if checkbox was clicked, for checkable grid.

* Highlight delete product batch rows with "pending customer orders" status.

* Add hover text for subdepartment name, in pricing batch row grid.


0.8.126 (2021-02-18)
--------------------

* Allow customization of main Buefy CSS styles, for falafel theme.

* Add special "contains any of" verb for string-based grid filters.

* Add special "equal to any of" verb for UPC-related grid filters.

* Tweaks per "delete products" batch.

* Misc. tweaks for vendor catalog batch.

* Add support for "default" trainwreck model.


0.8.125 (2021-02-10)
--------------------

* Fix some permission bugs when showing batch tools etc.

* Render batch execution description as markdown.

* Cleanup default display for vendor catalog batches.

* Make errors more obvious, when running batch commands as subprocess.

* Add styles for field labels in profile view.


0.8.124 (2021-02-04)
--------------------

* Fix bug when editing a Person.


0.8.123 (2021-02-04)
--------------------

* Fix config defaults for PurchaseView.

* Add stub methods for ``MasterView.template_kwargs_view()`` etc.

* Update references to vendor catalog batches etc.

* Fix display of handheld batch links, when viewing label batch.

* Prevent updates to batch rows, if batch is immutable.


0.8.122 (2021-02-01)
--------------------

* Normalize naming of all traditional master views.

* Undo recent ``base.css`` changes for ``<p>`` tags.

* Misc. improvements for ordering batches, purchases.

* Purge things for legacy (jquery) mobile, and unused template themes.

* Make handler responsible for possible receiving modes.

* Split "new receiving batch" process into 2 steps: choose, create.

* Add initial "scanning" feature for Ordering Batches.

* Add support for "nested" menu items.

* Add icon for Help button.


0.8.121 (2021-01-28)
--------------------

* Tweak how vendor link is rendered for readonly field.

* Use "People Handler" to update names, when editing person or user.


0.8.120 (2021-01-27)
--------------------

* Initial support for adding items to, executing customer order batch.

* Add changelog link for Theo, in upgrade package diff.

* Hide "collect from wild" button for UOMs unless user has permission.


0.8.119 (2021-01-25)
--------------------

* Don't create new person for new user, if one was selected.

* Allow newer zope.sqlalchemy package.

* Add variant transaction logic per zope.sqlalchemy 1.1 changes.

* Add CSS styles for 'codehilite' a la Pygments.

* Add feature to generate new features...

* Add views for "delete product" batch.

* Set ``self.model`` when constructing new View.

* Add some generic render methods to MasterView.

* Add custom ``base.css`` for falafel theme.

* Add master view for Units of Measure mapping table.

* Add woocommerce package links for sake of upgrade diff view.

* Add basic web API app, for simple use cases.


0.8.118 (2021-01-10)
--------------------

* Show node title in header for Login, About pages.

* Allow changing protected user password when acting as root.

* Allow specifying the size of a file, for ``readable_size()`` method.

* Try to show existing filename, for upload widget.

* Add basic support for "download" and "rawbytes" API views.


0.8.117 (2020-12-16)
--------------------

* Add common "form poster" logic, to make CSRF token/header names configurable.

* Refactor the feedback form to use common form poster logic.


0.8.116 (2020-12-15)
--------------------

* Add basic views for IFPS PLU Codes.

* Add very basic support for merging 2 People.

* Tweak spacing for header logo + title, in falafel theme.


0.8.115 (2020-12-04)
--------------------

* Add the "Employee Status" filter to People grid.

* Add "is empty" and related verbs, for "string" type grid filters.

* Assume composite PK when fetching instance for master view.


0.8.114 (2020-12-01)
--------------------

* Misc. tweaks to vendor catalog views.

* Tweak how an "enum" grid filter is initialized.

* Add "generic" Employee tab feature, for profile view.


0.8.113 (2020-10-13)
--------------------

* Tweak how global DB session is created.


0.8.112 (2020-09-29)
--------------------

* Add support for "list" type of app settings (w/ textarea).

* Add feature to "download rows for results" in master index view.

* Fix "refresh results" for batches, in Buefy theme.


0.8.111 (2020-09-25)
--------------------

* Allow alternate engine to act as 'default' when multiple are available.

* Fix grid bug when paginator is not involved.


0.8.110 (2020-09-24)
--------------------

* Add ``user_is_protected()`` method to core View class.

* Change how we protect certain person, employee records.

* Add global help URL to login template.

* Fix bug when fetching partial versions data grid.


0.8.109 (2020-09-22)
--------------------

* Add 'warning' class for 'delete' action in b-table grid.

* Add "worksheet file" pattern for editing batches.

* Avoid unhelpful error when perm check happens for "re-created" DB user.

* Prompt user if they try to send email preview w/ no address.

* Don't expose "timezone" for input when generating 'fabric' project.

* Add some more field hints when generating 'fabric' project.

* Show node title in header, for home page.

* Remove unwanted columns for default Products grid.


0.8.108 (2020-09-16)
--------------------

* Allow custom props for TailboneForm component.

* Remove some custom field labels for Vendor.

* Add support for generating new 'fabric' project.


0.8.107 (2020-09-14)
--------------------

* Stop including 'complete' filter by default for purchasing batches.

* Overhaul project changelog links for upgrade pkg diff table.

* Add support/views for generating new custom projects, via handler.


0.8.106 (2020-09-02)
--------------------

* Add progress for generating "results as CSV/XLSX" file to download.

* Use utf8 encoding when downloading results as CSV.

* Add new/flexible "download results" feature.

* Fix spacing between components in "grid tools" section.

* Add support for batch execution options in Buefy themes.

* Improve auto-handling of "local" timestamps.

* Expose ``Product.average_weight`` field.


0.8.105 (2020-08-21)
--------------------

* Tweaks for export views, to make more generic.

* Add config for "global" help URL.

* Remove ``<section>`` tag around "no results" for minimal b-table.

* Allow for unknown/missing "changed by" user for product price history.

* Add buefy theme support for ordering worksheet.

* Don't require department by default, for new purchasing batch.


0.8.104 (2020-08-17)
--------------------

* Make "download row results" a bit more generic.

* Add pagination to price, cost history grids for product view.


0.8.103 (2020-08-13)
--------------------

* Tweak config methods for customer master view.


0.8.102 (2020-08-10)
--------------------

* Improve rendering of ``true_margin`` column for pricing batch row grid.


0.8.101 (2020-08-09)
--------------------

* Fix missing scrollbar when version diff table is too wide for screen.

* Add basic web views for "new customer order" batches.

* Tweak the buefy autocomplete component a bit.

* Add basic/unfinished "new customer order" page/feature.

* Add ``protected_usernames()`` config function.

* Add ``model`` to global template context, plus ``h.maxlen()``.

* Coalesce on ``User.active`` when merging.

* Expose user reference(s) for employees.


0.8.100 (2020-07-30)
--------------------

* Add more customization hooks for making grid actions in master view.


0.8.99 (2020-07-29)
-------------------

* Add ``self.cloning`` convenience indicator for master view.

* Use handler ``do_delete()`` method when deleting a batch.


0.8.98 (2020-07-26)
-------------------

* Tweak field label for ``Product.item_id``.

* Make field list explicit for Department views.

* Make field list explicit for Store views.

* Don't allow "execute results" for any batches by default.

* Fix pagination sync issue with buefy grid tables.

* Fix permissions wiget bug when creating new role.

* Tweak "coalesce" logic for merging field data.


0.8.97 (2020-06-24)
-------------------

* Add dropdown, autohide magic when editing Role permissions.

* Add ability to download roles / permissions matrix as Excel file.

* Improve support for composite key in master view.

* Use byte string filters for row grid too.

* Convert mako directories to list, if it's a string.


0.8.96 (2020-06-17)
-------------------

* Don't allow edit/delete of rows, if master view says so.


0.8.95 (2020-05-27)
-------------------

* Cap version for 'cornice' dependency.

* Let each grid component have a custom name, if needed.


0.8.94 (2020-05-20)
-------------------

* Expose "shelved" field for pricing batches.

* Sort available reports by name, if handler doesn't specify.


0.8.93 (2020-05-15)
-------------------

* Parse pip requirements file ourselves, instead of using their internals.

* Don't auto-include "Guest" role when finding roles w/ permission X.


0.8.92 (2020-04-07)
-------------------

* Allow the home page to include quickie search.


0.8.91 (2020-04-06)
-------------------

* Add "danger" style for "delete" grid row action.

* Misc. API improvements for sake of mobile receiving.

* Use proper cornice service registration, for API batch execute etc.

* Add common permission for sending user feedback.

* Fix the "change password" form per Buefy theme.

* Expose the ``Role.notes`` field for view/edit.

* Add "local only" column to Users grid.

* Fix row status filter for Import/Export batches.

* Add "generic" ``render_id_str()`` method to MasterView.

* Stop raising an error if view doesn't define row grid columns.

* Add helper function, ``get_csrf_token()``.

* Add support for "choice" widget, for report params.

* Allow bulk-delete, merge for Brands table.

* Move inventory batch view to its proper location.

* Allow bulk-delete for Inventory Batches.

* Move "most" inventory batch logic out of view, to underlying handler.

* Add initial API views for inventory batches.

* Add basic dashboard page for TempMon.

* Let config totally disable the old/legacy jQuery mobile app.

* Defer fetching price, cost history when viewing product details.


0.8.90 (2020-03-18)
-------------------

* Add basic "ordering worksheet" API.

* Tweak GPC grid filter, to better handle spaces in user input.

* Only show tables for "public" schema.

* Remove old/unwanted Vue.js index experiment, for Users table.

* Misc. changes to User, Role permissions and management thereof.

* Don't let user delete roles to which they belong, without permission.

* Prevent deletion of department which still has products.

* Add sort/filter for Department Name, in Subdepartments grid.

* Allow "touch" for Department, Subdepartment.

* Expose ``Customer.number`` field.

* Add support for "bulk-delete" of Person table.

* Allow customization for Customers tab of Profile view.

* Expose default email address, phone number when editing a Person.

* Add/improve various display of Member data.


0.8.89 (2020-03-11)
-------------------

* Refactor "view profile" page per latest Buefy theme conventions.

* Move logic for Order Form worksheet into purchase batch handler.

* Make sure all contact info is "touched" when touching person record.


0.8.88 (2020-03-05)
-------------------

* Fix batch row status breakdown for Buefy themes.

* Add support for refreshing multiple batches (results) at once.

* Remove "api." prefix for default route names, in API master views.

* Allow "touch" for vendor records.


0.8.87 (2020-03-02)
-------------------

* Add new "master" API view class; refactor products and batches to use it.

* Refactor all API views thus far, to use new v2 master.

* Use Cornice when registering all "service" API views.


0.8.86 (2020-03-01)
-------------------

* Add toggle complete, more normalized row fields for odering batch API.

* Return employee_uuid along with user info, from API.

* Add support for executing ordering batches via API.

* Fix how we fetch employee history, for profile view.

* Cleanup main version history views for Buefy theme.

* Fix product price, cost history dialogs, for Buefy theme.

* Fix some basic product editing features.


0.8.85 (2020-02-26)
-------------------

* Overhaul the /ordering batch API somewhat; update docs.

* Tweak ``save_edit_row_form()`` of purchase batch view, to leverage handler.

* Tweak ``worksheet_update()`` of ordering batch view, to leverage handler.

* Fix "edit row" logic for ordering batch.

* Raise 404 not found instead of error, when user is not employee.

* Send batch params as part of normalized API.


0.8.84 (2020-02-21)
-------------------

* Add API view for changing current user password.

* Return new user permissions when logging in via API.


0.8.83 (2020-02-12)
-------------------

* Use new ``Email.obtain_sample_data()`` method when generating preview.

* Add some custom display logic for "current price" in pricing batch.

* Fix email preview for TXT templates on python3.

* Allow override of "email key" for user feedback, sent via API.

* Add way to prevent user login via API, per custom logic.

* Add common ``get_user_info()`` method for all API views.

* Return package names as list, from "about" page from API.


0.8.82 (2020-02-03)
-------------------

* Fix vendor ID/name for Excel download of pricing batch rows.

* Add red highlight for SRP breach, for generic product batch.

* Make sure falafel theme is somewhat available by default.


0.8.81 (2020-01-28)
-------------------

* Include regular price changes, for current price history dialog.

* Allow populate of new pricing batch from products w/ "SRP breach".

* Tweak how we import pip internal things, for upgrade view.

* Sort report options by name, when choosing which to generate.

* Add warning for "price breaches SRP" rows in pricing batch.


0.8.80 (2020-01-20)
-------------------

* Hide the SRP history link for new buefy themes.

* Add regular price history dialog for product view.

* Add support for Row Status Breakdown, for Import/Export batches.

* Cleanup "diff" table for importer batch row view, per Buefy theme.

* Highlight SRP in red, if reg price is greater.

* Expose batch ID, sequence for datasync change queue.

* Add "current price history" dialog for product view.

* Add "cost history" dialog for product view.


0.8.79 (2020-01-06)
-------------------

* Move "delete results" logic for master grid.


0.8.78 (2020-01-02)
-------------------

* Add ``Grid.set_filters_sequence()`` convenience method.

* Add dialog for viewing product SRP history.


0.8.77 (2019-12-04)
-------------------

* Use currency formatting for costs in vendor catalog batch.


0.8.76 (2019-12-02)
-------------------

* Allow update of row unit cost directly from receiving batch view.

* Show vendor item code in receiving batch row grid.

* Expose catalog cost, allow updating, for receiving batch rows.

* Add API view for marking "receiving complete" for receiving batch.

* Allow override of user authentication logic for API.

* Add API views for admin user to become / stop being "root".


0.8.75 (2019-11-19)
-------------------

* Filter by receiving mode, for receiving batch API.


0.8.74 (2019-11-15)
-------------------

* Add support for label batch "quick entry" API.

* Add support for "toggle complete" for batch API.

* Add some API views for receiving, and vendor autocomplete.

* Move "quick entry" logic for purchase batch, into rattail handler.

* Provide background color when first checking API session.


0.8.73 (2019-11-08)
-------------------

* Assume "local only" flag should be ON by default, for new objects.

* Bump default Buefy version to 0.8.2.

* Always store CSRF token for each page in Vue.js theme.

* Refactor "make batch from products query" per Vue.js theme.

* Add Vue.js support for "enable / disable selected" grid feature.

* Add Vue.js support for "delete selected" grid feature.

* Improve checkbox click handling support for grids.

* Improve/fix some views for Messages per Vue.js theme.

* Add some padding above/below form fields (for Vue.js).

* Use "warning" status for pricing batch rows, where product not found.

* Refactor "send new message" form, esp. recipients field, per Vue.js.

* Allow rendering of "raw" datetime as ISO date.

* Add very basic API views for label batches.

* Fallback to referrer if form has no cancel button URL.

* Fix merge feature for master index grid.


0.8.72 (2019-10-25)
-------------------

* Allow bulk delete of New Product batch rows.

* Don't bug out if can't update roles for user.


0.8.71 (2019-10-23)
-------------------

* Improve default behavior for clone operation.

* Add config flag to "force unit item" for inventory batch.

* Fix JS bug for graph view of tempmon probe readings.


0.8.70 (2019-10-17)
-------------------

* Don't bug out if stores, departments fields aren't present for Employee.


0.8.69 (2019-10-15)
-------------------

* Fix buefy grid pager bug.

* Fix permissions for add/edit/delete notes from people profile view.


0.8.68 (2019-10-14)
-------------------

* Use ``self.has_perm()`` within MasterView.

* Only show action URL if present, for Buefy grid rows.

* Show active flag for users mini-grid on Role view page.


0.8.67 (2019-10-12)
-------------------

* Fix URL for user, for feedback email.

* Add "is false or null" verb for boolean grid filters.

* Move label batch views to ``tailbone.views.batch.labels``.

* Allow bulk-delete for some common batches.

* Move vendor catalog batch views to ``tailbone.views.batch.vendorcatalog``.

* Expose the "is preferred vendor" flag for vendor catalog batches.

* Move vendor invoice batch views to ``tailbone.views.batch.vendorinvoice``.

* Expose unit cost diff for vendor invoice batch rows.

* Honor configured db key sequence; let config hide some db keys from UI.


0.8.66 (2019-10-08)
-------------------

* Fix label bug for grid filter with value choices dropdown.


0.8.65 (2019-10-07)
-------------------

* Add support for "local only" Person, User, plus related security.


0.8.64 (2019-10-04)
-------------------

* Add ``forbidden()`` convenience method to core View class.


0.8.63 (2019-10-02)
-------------------

* Fix "progress" behavior for upgrade page.


0.8.62 (2019-09-25)
-------------------

* Add core ``View.make_progress()`` method.


0.8.61 (2019-09-24)
-------------------

* Use ``simple_error()`` from rattail, for showing some error messages.

* Honor kwargs used for ``MasterView.get_index_url()``.

* Fix progress page so it effectively fetches progress data synchronously.

* Show "image not found" placeholder image for products which have none.


0.8.60 (2019-09-09)
-------------------

* Show product image from database, if it exists.

* Let config turn off display of "POD" image from products.


0.8.59 (2019-09-09)
-------------------

* Let a grid have custom ajax data url.

* Set default max height, width for app logo.

* Hopefully fix "single store" behavior when make a new ordering batch.

* Add basic support for create and update actions in API views.

* Tweak how we detect JSON request body instead of POST params.

* Add basic support for "between" verb, for date range grid filter.

* Add basic API view for user feedback.

* Add basic API view for "about" page.

* Include ``short_name`` in field list returned by /session API.

* Return current user permissions when session is checked via API.

* Tweak return value for /customers API.

* Cleanup styles for login form.

* Add /products API endpoint, enable basic filter support for API views.

* Add basic API endpoints for /ordering-batch.

* Don't show Delete Row button for executed batch, on jquery mobile site.

* Include tax1 thru tax3 flags in form fields for product view page.

* Prevent text wrap for pricing panel fields on product view page.

* Fix rendering of "handheld batches" field for inventory batch view.

* Fix various templates for generating reports, per Buefy.

* Fix 'about' page template for Buefy themes.


0.8.58 (2019-08-21)
-------------------

* Provide today's date as context for profile view.

* Tweak login page logo style for jQuery (non-Buefy) themes.


0.8.57 (2019-08-05)
-------------------

* Remove unused "login tips" for demo.

* Fix form handling for user feedback.

* Fix "last sold" field rendering for product view.


0.8.56 (2019-08-04)
-------------------

* Fix home and login pages for Buefy theme.


0.8.55 (2019-08-04)
-------------------

* Allow "touch" for Person records.

* Refactor Buefy templates to use WholePage and ThisPage components.

* Highlight former Employee records as red/warning.


0.8.54 (2019-07-31)
-------------------

* Freeze Buefy version at pre-0.8.0.


0.8.53 (2019-07-30)
-------------------

* Add proper support for composite primary key, in MasterView.


0.8.52 (2019-07-25)
-------------------

* Add 'disabled' prop for Buefy datepicker.

* Add perm for editing employee history from profile view.

* Add "multi-engine" support for Trainwreck transaction views.

* Cleanup 'phone' filter/sort logic for Employees grid.


0.8.51 (2019-07-13)
-------------------

* Add basic "DB picker" support, for views which allow multiple engines.

* Include employee history data in context for "view profile".

* Add custom permissions for People "profile" view.

* Use latest version of Buefy by default, for falafel theme.

* Send URL for viewing employee, along to profile page template.


0.8.50 (2019-07-09)
-------------------

* Add way to hide "view profile" helper for customer view.

* Add ``render_customer()`` method for MasterView.

* When creating an export, set creator to current user.

* Add basic "downloadable" support for ExportMasterView.

* Remove unwanted "export has file" logic for ExportMasterView.

* Refactor feedback dialog for Buefy themes.

* Add support for general "view click handler" for ``<b-table>`` element.


0.8.49 (2019-07-01)
-------------------

* Fix product view template per Buefy refactoring.


0.8.48 (2019-07-01)
-------------------

* Clear checked rows when refreshing async grid data.


0.8.47 (2019-07-01)
-------------------

* Allow "touch" for customer records.

* Add ``NumericInputWidget`` for use with Buefy themes.

* Expose a way to embed "raw" data values within Buefy grid data.

* Add 'duration_hours' type for grid column display.

* Make sure grid action links preserve white-space.


0.8.46 (2019-06-25)
-------------------

* Only expose "Make User" button when viewing a person.

* Fix PO total calculation bug for mobile ordering.

* Fix "edit row" icon for batch row grids, for Buefy themes.

* Refactor all Buefy form submit buttons, per Chrome behavior.


0.8.45 (2019-06-18)
-------------------

* Fix inheritance issue with "view row" master template.


0.8.44 (2019-06-18)
-------------------

* Add generic ``/page.mako`` template.

* Add Buefy support for "execute results" from core batch grid view.

* Pull the grid tools to the right, for Buefy.

* Fix click behavior for all/diffs package links in upgrade view.

* Refactor form/page component structure for Buefy/Vue.js.


0.8.43 (2019-06-16)
-------------------

* Refactor tempmon probe view template, per Buefy.

* Refactor tempmon probe graph view per Buefy.

* Use once-button for tempmon client restart.

* Fix package diff table for upgrade view template, per Buefy.

* Assign client IP address to session, for sake of data versioning.

* Use locale formatting for some numbers in the Buefy grid.

* Buefy support for "mark batch as (in)complete".


0.8.42 (2019-06-14)
-------------------

* Fix some response headers per python 3.

* Make person, created by fields readonly when editing Person Note.


0.8.41 (2019-06-13)
-------------------

* Add ``json_response()`` convenience method for all views.

* Add ``<b-table>`` element template for simple grids with "static" data.

* Improve props handling for ``<once-button>`` component.

* Fall back to parsing request body as JSON for form data.

* Basic support for maintaining PersonNote data from profile view.

* Fix permissions styles for view/edit of User, Role.

* Turn on bulk-delete feature for Raw Settings view.

* Add a generic "user" field renderer to master view.

* Fix "current value" for ``<b-select>`` element in e.g. edit form views.

* Use ``<once-button>`` in more places, where appropriate.

* Update calculated PO totals for purchasing batch, when editing row.

* Add support for Buefy autocomplete.

* More Buefy tweaks, for file upload, and "edit batch" generally.

* Tweak structure of "view product" page to support Buefy, context menu.

* Add support for "simple confirm" of object deletion.

* Add some vendor fields for product Excel download.


0.8.40 (2019-06-03)
-------------------

* Add ``verbose`` flag for ``util.raw_datetime()`` rendering.

* Add basic master view for PersonNote data model.

* Make email preview buttons use primary color.

* Add basic Buefy support for batch refresh, execute buttons.

* Add basic/generic Buefy support to the Form class.

* Add custom ``tailbone-datepicker`` component for Buefy.

* Let view template define how to render "row grid tools".

* Move logic used to determine if current request should use Buefy.

* Allow inherited theme to set location of Vue.js, Buefy etc.

* Add "full justify" for grid filter pseudo-column elements.

* Expose per-page size picker for Buefy grids.

* Add basic Buefy support for default SelectWidget template.

* Add Buefy support for enum grid filters.

* Add ``<once-button>`` component for Buefy templates.

* Add basic Buefy support for "Make User" button when viewing Person.

* Make Buefy grids use proper Vue.js component structure.

* Assume forms support Buefy if theme does; fix basic CRUD views.

* Fix Buefy "row grids" when viewing parent; add basic file upload support.

* Refactor "edit printer settings" view for Label Profile.

* Add Buefy panels support for "view product" page.

* Allow bulk row delete for generic products batch.

* also "lots more changes" for sake of Buefy support...


0.8.39 (2019-05-09)
-------------------

* Expose params and type key for report output.

* Clean up falafel theme, move some parts to root template path.

* Allow choosing report from simple list, when generating new.

* Force unicode string behavior for left/right arrow thingies.

* Must still define "jquery theme" for falafel theme, for now.

* Add support for "quickie" search in falafel theme.

* Fix sorting info bug when Buefy grid doesn't support it.

* Make "view profile" buttons use "primary" color.

* Add ``simple_field()`` def for base falafel template.

* Align pseudo-columns for grid filters; let app settings define widths.

* Tweak how we disable grid filter options.

* Add basic Buefy form support when generating reports.

* Add basic/generic email validator logic.


0.8.38 (2019-05-07)
-------------------

* Add basic support for "quickie" search.

* Add basic Buefy support for row grids.

* Add basic Buefy support for merging 2 objects.


0.8.37 (2019-05-05)
-------------------

* Add basic Buefy support for full "profile" view for Person.


0.8.36 (2019-05-03)
-------------------

* Add basic support for "touching" a data record object.


0.8.35 (2019-04-30)
-------------------

* Add filter for Vendor ID in Pricing Batch row grid.

* Pass batch execution kwargs when doing that via subprocess.


0.8.34 (2019-04-25)
-------------------

* Don't assume grid model class declares its title.


0.8.33 (2019-04-25)
-------------------

* Add "most of" Buefy support for grid filters.

* Add Buefy support for email preview buttons.

* Improve logic used to determine if current theme supports Buefy.

* Add basic Buefy support for App Settings page.

* Add views for "new product" batches.

* Fix auto-disable action for new message form.

* Declare row fields for vendor catalog batches.

* Add "created by" and "executed by" grid filters for all batch views.

* Expose new code fields for pricing batch.

* Add basic Buefy support for "find user/role with permission X".

* Improve default people "profile" view somewhat.

* Add support for generic "product" batch type.

* Fix some issues with progress "socket" workaround for batches.

* Allow config to specify grid "page size" options.

* Add ``render_person()`` convenience method for MasterView.


0.8.32 (2019-04-12)
-------------------

* Can finally assume "simple" menus by default.

* Add custom grid filter for phone number fields.

* Add ``raw_datetime()`` function to ``tailbone.helpers`` module.

* Add "profile" view, for viewing *all* details of a given person at once.

* Add "view profile" object helper for all person-related views.

* Hopefully fix style bug when new filter is added to grid.


0.8.31 (2019-04-02)
-------------------

* Require invoice parser selection for new truck dump child from invoice.

* Make sure user sees "receive row" page on mobile, after scanning UPC.

* Use shipped instead of ordered, for receiving authority.

* Add ``move_before()`` convenience method for ``GridFilterSet``.


0.8.30 (2019-03-29)
-------------------

* Add smarts for some more projects in the upgraded packages links.

* Add basic "Buefy" support for grids (master index view).

* Remove 'number' column for Customers grid by default.

* Add feature for generating new report of arbitrary type and params.

* Fix rendering bug when ``price.multiple`` is null.

* Fix HTML escaping bug when rendering products with pack price.

* Don't allow deletion of some receiving data rows on mobile.

* Add validation when "declaring credit" for receiving batch row.

* Add proper hamburger menu for falafel theme.

* Add icon for Feedback button, in falafel theme.


0.8.29 (2019-03-21)
-------------------

* Allow width of object helper panel to grow.


0.8.28 (2019-03-14)
-------------------

* Tweak how batch handler is invoked to remove row.

* Add mobile alert when receiving product for 2nd time.

* Honor enum sort order where possible, for grid filter values.

* Add basic "receive row" desktop view for receiving batches.

* Add "declare credit" UI for receiving batch rows.


0.8.27 (2019-03-11)
-------------------

* Fix some unicode literals for base template.


0.8.26 (2019-03-11)
-------------------

* Expose "true cost" and "true margin" columns for products grid.

* Use configured background color for 'bobcat' theme.

* Add view, edit links to vue.js users index.

* Fix navbar, footer background to match custom body background (bobcat theme).

* Fix layout issues for bobcat theme, so footer sticks to bottom.

* Fix login page styles for bobcat theme.

* Refactor template ``content_title()`` and prev/next buttons feature.

* Add basic 'dodo' theme.

* Allow apps to set background color per request.

* Add 'falafel' theme, based on bobcat.

* Begin to customize grid filters, for 'falafel' theme.

* Fix PO unit cost calculation for ordering row, batch.


0.8.25 (2019-03-08)
-------------------

* Show grid link even when value is "false-ish".

* Only objectify address data if present.

* Improve display of purchase credit data.

* Expose new "calculated" invoice totals for receiving batch, rows.


0.8.24 (2019-03-06)
-------------------

* Add "plain" date widget.

* Invoke handler when marking batch as (in)complete.

* Add new "receive row" view for mobile receiving; invokes handler.

* Remove 'truck_dump' field from mobile receiving batch view.

* Add "truck dump status" fields to receiving batch views.

* Add ability to sort by Credits? column for receiving batch rows.

* Add mobile support for basic "feedback" dialog.

* Tweak the "incomplete" row filter for mobile receiving batch.


0.8.23 (2019-02-22)
-------------------

* Add basic support for "mobile edit" of records.

* Add basic support for editing address for a "contact" record.

* Add ``unique_id()`` validator method to Customer view.

* Declare "is contact" for the Customers view.

* Allow vendor field to be dropdown, for mobile ordering/receiving.

* Treat empty string as null, for app settings field values.


0.8.22 (2019-02-14)
-------------------

* Improve validator for "percent" input widget.

* Refactor email settings/preview views to use email handler.


0.8.21 (2019-02-12)
-------------------

* Remove usage of ``colander.timeparse()`` function.


0.8.20 (2019-02-08)
-------------------

* Introduce support for "children first" truck dump receiving.


0.8.19 (2019-02-06)
-------------------

* Add support for downloading batch rows as XLSX file.


0.8.18 (2019-02-05)
-------------------

* Add support for "delete set" feature for main object index view.

* Use app node title setting for base template.

* Improve user form handling, to prevent unwanted Person creation.

* Add support for background color app setting.

* Add generic support for "enable/disable selection" of grid records.


0.8.17 (2019-01-31)
-------------------

* Improve rendering of ``enabled`` field for tempmon clients, probes.


0.8.16 (2019-01-28)
-------------------

* Update tempmon UI now that ``enabled`` flags are really datetime in DB.


0.8.15 (2019-01-24)
-------------------

* Fix response header value, per python3.


0.8.14 (2019-01-23)
-------------------

* Use empty string for "missing" department name, for ordering worksheet.


0.8.13 (2019-01-22)
-------------------

* Include ``robots.txt`` in the manifest.


0.8.12 (2019-01-21)
-------------------

* Log details of one-off label printing error, when they occur.

* Fix Excel download of ordering batch, per python3.


0.8.11 (2019-01-17)
-------------------

* Convert all datetime values to localtime, for "download rows as CSV".


0.8.10 (2019-01-11)
-------------------

* Fix products grid query when filter/sort has multiple ProductCost joins.


0.8.9 (2019-01-10)
------------------

* Tweak batch view template "object helpers" for easier customization.

* Let batch view customize logic for marking batch as (in)complete.

* Make command configurable, for restarting tempmon-client.


0.8.8 (2019-01-08)
------------------

* Add custom widget for "percent" field.


0.8.7 (2019-01-07)
------------------

* Fix styles for master view_row template.

* Turn off messaging-related menus by default.


0.8.6 (2019-01-02)
------------------

* Expose ``vendor_id`` column in pricing batch row grid.

* Only allow POST method for executing "results" for batch grid.


0.8.5 (2019-01-01)
------------------

* Add basic master view for Members table.


0.8.4 (2018-12-19)
------------------

* Add ``object_helpers()`` def to master/view template.

* Add ``oneoff_import()`` helper method to MasterView class.

* Fix some styles, per flexbox layout changes.

* Add ability to make new pricing batch from input data file.

* Clean up some inventory batch UI logic; prefer units by default.

* Add 'unit_cost' to Excel download for Products grid.

* Expose subdepartment for pricing batch rows.

* Add 'percent' as field type for Form; fix rendering of 'percent' for Grid.

* Expose label profile selection when editing label batch.

* Make sure custom field labels are shown for batch execution dialog.


0.8.3 (2018-12-14)
------------------

* Fix some layout styles for master edit template.


0.8.2 (2018-12-13)
------------------

* Refactor product view template to use flexbox styles.


0.8.1 (2018-12-10)
------------------

* Expose new "sync me" flag for LabelProfile settings.


0.8.0 (2018-12-02)
------------------

This version begins the "serious" efforts in pursuit of REST API, Vue.js, Bulma
and related technologies.

* Use sqlalchemy-filters package for REST API collection_get.

* Refactor API collection_get to work with vue-tables-2.

* Remove some relationship fields when creating new Person.

* Fix bug in receiving template when truck dump not enabled.

* Tweak default "model title" logic for master view.

* Add better support for "make import batch from file" pattern.

* Fix download filename when it contains spaces.

* Add "min % diff" option for pricing batch from products query.

* Allow override of products query when making batch from it.

* Use empty string instead of null as fallback value, for pricing rows CSV.

* Add very basic Vue.js grid/index experiment for Users table.

* Add patterns for joining tables in API list methods.

* Add template "theme" feature, albeit global.

* Clean up how we configure DB sessions on app startup.

* Add description, notes to default form_fields for batch views.

* Add basic 'excite-bike' theme.

* Use Bulma CSS and some components for 'bobcat' theme.

* Add basic support for "simple menus".

* Refactor default theme re: "context menu" and "object helper" styles.

* Use 4 decimal places when calculating hours for worked shift excel download.

* Expose ``old_price_margin`` field for pricing batch rows.


0.7.50 (2018-11-19)
-------------------

* Add simple price fields for product XLSX results download.

* Add "200 per page" option for UI table grids.

* Add department, subdepartment "name" columns for products XLSX download.

* Allow override of template for custom create views.

* Expose new ``Customer.wholesale`` flag.

* Add vendor id, name to row CSV download for pricing batch.

* Expose ``suggested_price``, ``price_diff_percent``, ``margin_diff`` for
  pricing batch row.


0.7.49 (2018-11-08)
-------------------

* Detect non-numeric entry when locating row for purchase batch.

* Remove unwanted style for "email setting description" field.

* Add ``Grid.hide_columns()`` convenience method.

* Make sure status field is readonly when creating new batch.

* Display "suggested price" when viewing product details.


0.7.48 (2018-11-07)
-------------------

* Add initial ``tailbone.api`` subpackage, with some basic API views.  Note
  that this API is meant to be ran as a separate app so we can better leverage
  Cornice features.

* Add client IP address to user feedback email.


0.7.47 (2018-10-25)
-------------------

* Try to configure the 'pyramid_retry' package, if available.

* Add more time range options for viewing tempmon probe readings as graph.

* Add button for restarting filemon.


0.7.46 (2018-10-24)
-------------------

* Allow individual App Settings to not be required; allow null.

* Add ``MasterView.render_product()``; fix edit for pricing batch row.

* Add ability to "transform" TD parent row from pack to unit item.


0.7.45 (2018-10-19)
-------------------

* Add very basic support for viewing tempmon probe readings as graph.


0.7.44 (2018-10-19)
-------------------

* Don't include LargeBinary properties in default colander schema.


0.7.43 (2018-10-19)
-------------------

* Add new timeout fields for tempmon probe.

* Customize template for viewing probe details.

* Add support for new Tempmon Appliance table, etc.

* Add basic image upload support for tempmon appliances.

* Add thumbnail images to Appliances grid.

* Hopefully, let the Grid class generate a default list of columns.

* Don't include grid filters for LargeBinary columns.


0.7.42 (2018-10-18)
-------------------

* Fix a dialog button for Chrome.


0.7.41 (2018-10-17)
-------------------

* Cache user permissions upon "new request" event.

* Add basic Excel download support for Products table.


0.7.40 (2018-10-13)
-------------------

* Add "hours as decimal" hover text for some HH:MM timesheet values.


0.7.39 (2018-10-09)
-------------------

* Fix bug when non-numeric entry given for mobile inventory "quick row".

* Show tempmon readings when viewing client or probe.

* Auto-disable button when sending email preview.

* Add some helptext for various tempmon fields.

* Allow override of jquery for base templates, desktop and mobile.

* Improve "length" (hours) column for Worked Shifts grid.

* Add basic Excel download support for raw worked shifts.


0.7.38 (2018-10-03)
-------------------

* Add support for "archived" flag in Tempmon Client views.

* Expose notes field for tempmon client and probe views.

* Expose new ``disk_type`` field for tempmon client views.

* Tweak how receiving rows are looked up when adding to the batch.


0.7.37 (2018-09-27)
-------------------

* Restrict (temporarily I hope) webhelpers2_grid to 0.1.


0.7.36 (2018-09-26)
-------------------

* Leverage alternate code also, for mobile product quick lookup.

* Misc. UI improvements for truck dump receiving on desktop.

* Add speedbump by default when deleting any "row" record.

* Expose ``item_entry`` field for receiving batch row.

* Capture user input for mobile receiving, and move some lookup logic.


0.7.35 (2018-09-20)
-------------------

* Fix batch row status breakdown, for rows with no status.


0.7.34 (2018-09-20)
-------------------

* Add unique check for "name" when creating new Role.

* Fix bug when editing truck dump child batch row quantities.

* Add setting to show/hide product image for mobile purchasing/receiving.

* Show red background for mobile receiving if product not found.

* Add quick-receive 1EA, 3EA, 6EA for mobile receiving.

* Fix how we check config for mobile "quick receive" feature.

* Do quick lookup by vendor item code, alt code for mobile receiving.

* Fix price fields, add pref. vendor/cost fields for mobile product view.

* Add simple row status breakdown when viewing batch.

* Only show mobile "quick receive" buttons if product is identifiable.


0.7.33 (2018-09-10)
-------------------

* Fix default (status) filter for Employees grid.


0.7.32 (2018-08-24)
-------------------

* Add "quick receive all" support for mobile receiving.

* Refactor sqlerror tween to add support for pyramid_retry.

* Honor view logic when displaying Delete Row button for mobile receiving.


0.7.31 (2018-08-14)
-------------------

* Make sure we refresh batch status when adding a new row.

* Hide 'ordered' columns for truck dump parent row grid.

* Add support for editing "claim" quantities for truck dump child row.

* Use invoice total, PO total as fallback, for mobile receiving list.

* Show links to claiming rows for truck dump parent row.

* Add "quick lookup" for mobile Products page.


0.7.30 (2018-07-31)
-------------------

* Don't configure versioning when making the app.


0.7.29 (2018-07-30)
-------------------

* Various tweaks for arbitrary model view with "rows".


0.7.28 (2018-07-26)
-------------------

* Let mobile form declare if/how to auto-focus a field.

* Assign purchase to new receiving batch via uuid instead of object ref.

* Fix permission group label for Ordering Batches.

* Redirect to "view parent" after deleting a row.


0.7.27 (2018-07-19)
-------------------

* Use upload time as default filter/sort for Trainwreck transactions.

* Add initial support for mobile "quick row" feature, for ordering.

* Add product grid filters for "on hand", "on order".

* Don't make customer ID readonly when editing.

* Fix Person.customers readonly field for python 3.

* Traverse master class hierarchy to collect all defined labels.

* Add 'person' column for customers grid.

* Fix how we check file size when reading stdout for upgrade.

* Add runtime ``mobile`` flag for ``MasterView``.

* Improve basic mobile views for customers, people.

* Refactor mobile receiving to use "quick row" feature.

* Improve support for "receive from scratch" workflow, esp. for mobile.

* Add (admin-friendly!) view to manage some App Settings.

* Add (restore?) basic support for mobile receiving from PO.

* Expose status etc. when editing upgrade; rename Email Settings.


0.7.26 (2018-07-11)
-------------------

* Force user to count "units" and not "packs" for inventory batch.

* Fix bug for inventory batch when product not found.

* Sort mobile receiving rows by last modified instead of sequence.

* Tweak default page title for master view.

* Show "truck dump" info for applicable receiving batch page title.

* Highlight purchasing batch rows with "case quantity differs" status.

* Improve how cases/units, uom are handled for mobile receiving.

* Add "?" for daily time sheet total if partial shift present.

* Fix cancel button for progress page.


0.7.25 (2018-07-09)
-------------------

* Fix enum values for customer email preference grid filter.

* Tweak field ordering for customer form.

* Remove deprecated "edbob" settings.

* Improve basic support for unit/pack info when viewing product details.


0.7.24 (2018-07-03)
-------------------

* Tweak how some "pack item" fields are displayed when viewing product.


0.7.23 (2018-07-03)
-------------------

* Don't read upgrade progress file if size hasn't changed.

* Fix batch file download link URL.

* Fix batch action kwargs, so 'action' can be a handler kwarg.


0.7.22 (2018-06-29)
-------------------

* Consider any integer greater than PG allows, to be invalid grid filter value.


0.7.21 (2018-06-28)
-------------------

* Fix bug when populating new batch.

* Allow zero quantity for inventory batch rows.

* Allow editing of unit cost for inventory batch row.

* Add overflow validation for cases/units in inventory batch desktop form.

* Add ``credit_total`` column for purchase credits grid.

* Don't aggregate product for mobile truck dump receiving.

* Be smarter about when we sort receiving batch by most recent (for mobile).

* Accept invoice number when adding truck dump child from invoice file.

* Add highlight for "cost not found" rows in purchasing batch.

* Fix email preview logic per python 3.

* Improve basic support for adding new product.

* Show department column for receiving batch rows.

* Fix how "unknown product" row is added to receiving batch.


0.7.20 (2018-06-27)
-------------------

* Fix input validation for integer grid filter.


0.7.19 (2018-06-14)
-------------------

* Change how date fields are handled within grid filters.

* Add workaround for using pip 10.0 "internal" API in upgrades view.


0.7.18 (2018-06-14)
-------------------

* Auto-size columns for Excel results download.

* Add Excel results download for categories, report codes.

* Use "known" label if possible when making new grid filters.

* Expose new ``exempt_from_gross_sales`` flags.


0.7.17 (2018-06-09)
-------------------

* Allow products view to set some labels in costs grid.

* Let config override ``sys.prefix`` when launching batch commands in subprocess.


0.7.16 (2018-06-07)
-------------------

* Add versioning workaround support for batch actions.


0.7.15 (2018-06-05)
-------------------

* Add integer-specific grid filter.

* Set filter value renderer when setting enum for grid field.


0.7.14 (2018-06-04)
-------------------

* Show department instead of subdept by default, for products grid.

* Add support for variance inventory batches, aggregation by product.

* Set default column renderers for grid based on data types.

* Expose 'hidden' flag for inventory adjustment reasons.

* Expose new ``Vendor.abbreviation`` field.


0.7.13 (2018-05-31)
-------------------

* Show 'variance' field when viewing inventory batch row.


0.7.12 (2018-05-30)
-------------------

* Make sure count mode is preserved when making new inventory batch.

* Add initial support for "variance" inventory batch mode.

* Fix handling of (missing) password when user is edited.


0.7.11 (2018-05-25)
-------------------

* Add ``Form.__contains__()`` method.

* Improve default behavior for receiving a purchase batch.

* Fix label profile type field when editing label batch row.

* Allow lookup of inventory item by alternate code.

* Fix rowcount bug when first row added via ordering worksheet.

* Add "most of" support for truck dump receiving.

* Add docs for ``MasterView.help_url`` and ``get_help_url()``.

* Add "Receive 1 CS" button for better efficiency in mobile receiving.

* Add category name filter for products grid.

* Increase allowed width for form labels.

* Add ``allow_zero_all`` flag for inventory batch master.

* Add buttons to toggle batch 'complete' flag when viewing batch.

* Hide "create new row" link for batches which are marked complete.

* Add way to prevent "case" entries for inventory adjustment batch.

* Add ``MasterView.use_byte_string_filters`` flag for encoding search values.


0.7.10 (2018-05-02)
-------------------

* Add sort/filter for department name, for Categories grid.


0.7.9 (2018-04-12)
------------------

* Add future mode for vendor catalog batch.


0.7.8 (2018-04-09)
------------------

* Add awareness for ``Email.dynamic_to`` flag in config UI.

* Add new vendor catalog row status, render product with hyperlink.


0.7.7 (2018-03-23)
------------------

* Use 'today' as fallback order date for ordering worksheet.

* Treat unknown UPC as "product not found" for inventory batch.

* Refactor inventory batch desktop lookup, to allow for Type 2 UPC logic.

* Fix default selection bug for store/department time sheet filters.


0.7.6 (2018-03-15)
------------------

* Fix text area behavior for email recipient fields.

* Fix autodisable button bug for forms marked as such.


0.7.5 (2018-03-12)
------------------

* Add desktop support for creating inventory batches.

* Expose vendor item code for purchase credits.

* Fix default create logic for vendors, products.

* Add changelog link for rattail-tempmon in upgrade diff.

* Add ``disable_submit_button()`` global JS function.

* Add basic support for making new product on-the-fly during mobile ordering.


0.7.4 (2018-02-27)
------------------

* Use all "normal" product form fields, for mobile view.

* Refactor ordering worksheet to use shared logic.

* Add download path for batch master views.

* Add basic mobile support for executing batches (with options).

* Add ``NumberInputWidget`` for ``<input type="number" />``.

* Add ``Form.mobile`` flag and set link button styles accordingly.

* Always show flash-error-style message when form has errors.

* Use ``Form.submit_label`` if present, or fall back to ``save_label``.

* Expose ``ship_method`` and ``notes_to_vendor`` for purchase, ordering batch.

* Bind batch to its execution options schema, when applicable.

* Don't set order date for new ordering batch when created via mobile.

* Don't allow row deletion if batch is marked complete.

* Add logic for editing default phone/email in base master view.

* Fix bug in users view when person field not present.


0.7.3 (2018-02-15)
------------------

* More tweaks for python 3.


0.7.2 (2018-02-14)
------------------

* Refactor all remaining forms to use colander/deform.

* Coalesce 'forms2' => 'forms' package.

* Remove dependencies: FormAlchemy, FormEncode, pyramid_simpleform, pyramid_debugtoolbar

* Misc. cleanup for Python 3.

* Add generic 'login_as_home' setting.

* Add tailbone version to base stylesheet URLs.


0.7.1 (2018-02-10)
------------------

* Make it easier to hide buttons for a form.

* Let forms choose *not* to auto-disable their cancel button.

* Add 'newstyle' behavior for ``Form.validate()``.

* Add some basic ORM object field types for new forms.

* Make sure each grid has unique set of actions.

* Add 'gridcore' jQuery plugin, for core behavior.

* Allow passing arbitrary attrs when rendering grid.

* Refactor mobile receiving to use colander/deform.

* Refactor mobile inventory to use colander/deform.

* Refactor user login, change password to use colander/deform.

* Fix some bugs with importer batch views.


0.7.0 (2018-02-07)
------------------

* Coalesce all master views back to single base class.

* Add ``append()`` and ``replace()`` methods for core Grid class.

* Show year dropdown by default for jQuery UI date pickers.

* Don't process file for new batch unless field is present.

* Add setting for "force home" mobile behavior.

* Add 'plain' and 'jquery' templates for deform select widget.

* Add "hidden" concept for form fields.

* Add ``Form.show_cancel`` flag, for hiding that button.

* Let each form define its "save" button text.

* Add master view for ``EmailAttempt``.

* Avoid "auto disable" button logic for new message form.

* Add better UPC validation for mobile receiving.


0.6.69 (2018-02-01)
-------------------

* Add proper enum for inventory batch "count mode" filter.

* Fix bugs when making inventory batch on mobile.


0.6.68 (2018-01-31)
-------------------

* Cap zope.sqlalchemy dependency at pre-1.0.


0.6.67 (2018-01-30)
-------------------

* Fix permission bug when adding row in mobile receiving.

* Fix mobile logout behavior.

* Always redirect to mobile home page, if "other" page is refreshed.


0.6.66 (2018-01-29)
-------------------

* Add support for detaching Person from Customer.

* Allow disabling auto-dismiss of flash messages on mobile.

* Add ``FieldList`` wrapper for grid columns list.

* Show "unit cost" column by default, for products grid.

* Improve case/unit quantity validation for order worksheet.

* Show new 'confirmed' field for brands table.

* Add support for extra column(s) in timesheet view table.

* Add generic "download results as XLSX" feature.

* Add vendor links in cost grid when viewing product.

* Show "buttons" when viewing an object, with forms2 (i.e. Execute Batch).

* Refactor "most" remaining batch views etc. to use master3.


0.6.65 (2018-01-24)
-------------------

* Fix some master3 edit issues for products view.

* Let custom inventory batch view override logic for mobile UPC scanning.

* Show new ``cashback`` field for Trainwreck transaction.

* Add 'delete-instance' class to delete link when viewing a record.


0.6.64 (2018-01-22)
-------------------

* Warn if user "scans" UPC with more than 14 digits, for mobile inventory.

* Add option for preventing new inventory batch rows for unknown products.

* Add ``creates_multiple`` flag for master view.

* Add basic support for per-page help URL.


0.6.63 (2018-01-16)
-------------------

* Fix bug when locating association proxy column.

* Fix client field when creating / editing tempmon probe.

* Allow editing of inventory batch count mode and reason code.


0.6.62 (2018-01-11)
-------------------

* Fix dialog button click event when executing price batch (for Chrome).

* Fix some mobile view URLs.

* Show case quantity for inventory batch rows.

* Let custom schema node start out with empty children.

* Allow passing None to ``Form.set_renderer()``.


0.6.61 (2018-01-11)
-------------------

* Provide some default readonly form field renderers.

* Fix row query bug when deleting batch row.


0.6.60 (2018-01-10)
-------------------

* Refactor several straggler views to use master3.

* Add first attempt at master3 for batch views.


0.6.59 (2018-01-08)
-------------------

* Fix bug when printing product label.


0.6.58 (2018-01-08)
-------------------

* Tweak diff styles when viewing upgrade.


0.6.57 (2018-01-07)
-------------------

* Fix some styles for execution options dialog.

* Show 'static_prices' flag for label batches.

* Add field name as wrapper class name.

* Change how select menus are enhanced for batch exec options.

* Add view for InventoryAdjustmentReason model.

* Stop setting execution details when multiple batches executed.

* Add empty default when displaying values in grid.

* Let grids be paginated even when they have no model class.

* Exclude JS for refreshing batch unless it's relevant.

* Tweak conditions for CSV row download link.

* Add basic support for row grid view links.

* Refactor away the ``row_route_prefix`` concept.

* Add ``row_title`` to template context for ``view_row``.

* Tweak ``diffs.css`` and refactor 'view_version' template to use it.

* Add basic UI support for "importer batch" feature.


0.6.56 (2018-01-05)
-------------------

* Fix bug when making batch from product query.


0.6.55 (2018-01-04)
-------------------

* Add "price required" flag to product view.

* Add a bit more flexibility to jquery time input values.

* Show row count field when viewing vendor catalog batch.

* Tweak product filter for report code name.

* Refactor forms logic when making batch from product query.


0.6.54 (2017-12-20)
-------------------

* Provide sane width for filter value dropdowns.


0.6.53 (2017-12-19)
-------------------

* Accept ``value_enum`` kwarg when creating grid filter.


0.6.52 (2017-12-08)
-------------------

* Add transaction "System ID" field for Trainwreck.

* Add ``Grid.set_sort_defaults()`` method.

* Change template prefix for vendor catalog batches.

* Add basic "helptext" support for forms2.

* Add cleared/selected callbacks for jquery autocomplete in forms2.

* Add ``Grid.remove_filter()`` method.

* Add custom schema type for jQuery time picker data.

* Refactor lots of views to use master3.


0.6.51 (2017-12-03)
-------------------

* Refactor customers view to use master3.

* Add custom ``FieldList`` class for forms2 field list.

* Auto-scroll window as needed to ensure drop-down choices are visible.

* Hide status when creating new purchasing batch.

* Add "manually priced" awareness to pricing batch UI.

* Add batch description to page body title.

* Fix batch row count when bulk-deleting rows.

* Allow bulk delete of label batch rows.

* Expose description and notes for label batches.

* Let batch views allow or deny "execute results" option.

* Allow "execute results" for inventory batches.

* Fix permission bug for mobile inventory batch.

* Expose default address for customers view.


0.6.50 (2017-11-21)
-------------------

* Set widget when defining enum for a form2 field.

* Add date/time-picker, autocomplete support for forms2 (deform).

* Add colander magic for association proxy fields.


0.6.49 (2017-11-19)
-------------------

* Improve auto-disable logic for some form buttons.

* Fix (hack) for editing some department flags.


0.6.48 (2017-11-11)
-------------------

* Accept ``None`` as valid arg for ``Grid.set_filter()``.


0.6.47 (2017-11-08)
-------------------

* Fix manifest to include *.pt deform templates


0.6.46 (2017-11-08)
-------------------

* Add ``json`` to global template context


0.6.45 (2017-11-01)
-------------------

* Add product and personnel flags for Department

* Add sorters, filters for Product regular, current price

* Add "text" type for new form fields

* Add description, notes for pricing batches


0.6.44 (2017-10-29)
-------------------

* Fix join bug for Upgrades table when sorting by executor


0.6.43 (2017-10-29)
-------------------

* Add "make user" button when viewing person w/ no user account


0.6.42 (2017-10-28)
-------------------

* Add cashier info, upload time for Trainwreck transaction views


0.6.41 (2017-10-25)
-------------------

* Add support for validator and required flag, for new forms

* Use master3 view for datasync changes


0.6.40 (2017-10-24)
-------------------

* Add grid filter which treats empty string as NULL

* Fix value auto-selection for enum grid filters

* Add ``item_id`` to trainwreck views

* Expose ``Person.users`` relationship (readonly)


0.6.39 (2017-10-20)
-------------------

* Fix bug with products view config


0.6.38 (2017-10-19)
-------------------

* Add "local" datetime renderer for new grids, forms

* Make CSRF protection optional (but on by default)

* Convert user feedback mechanism to use modal dialog

* Add 'active' column to Users table view

* Add "download row results as CSV" feature to master view

* Add support for setting default field values on new forms

* Add 'currency' field type for new forms

* Allow passing ``None`` to ``Grid.set_joiner()``


0.6.37 (2017-09-28)
-------------------

* Fix data type/size issue with CSV download

* Don't set batch input file on creation, if no file exists

* Add "auto-enhance" select field template for deform

* Add ability to override schema node for custom deform fields

* Fix deform widget resource inclusion for master/create template

* Pass form along to ``before_create_flush()`` in master3

* Add "populatable" for master views (populating new objects with progress)

* Add 'duration' type for new form fields


0.6.36 (2017-09-15)
-------------------

* Fix user field rendering when no person associated

* Add generic support for downloading list results as CSV

* Tweak title for master view row template


0.6.35 (2017-08-30)
-------------------

* Fix some bugs for rendering upgrade package diffs


0.6.34 (2017-08-18)
-------------------

* Fix mobile inventory template

* Add extra perms for creating inventory batch w/ different modes

* Allow batch execution to require options on a per-batch basis

* Convert more views to master3:
  departments, subdepartments, categories, brands, bouncer, customer groups

* Override deform template for checkbox field; fix label behavior

* Show all grid actions by default, if there are 3 or less

* Use shared logic for executing upgrade


0.6.33 (2017-08-16)
-------------------

* Add ``LocalDateTimeFieldRenderer`` for formalchemy

* Fix auto-disable button on form submit, per Chrome issues


0.6.32 (2017-08-15)
-------------------

* Add generic changelog link for rattail/tailbone packages

* Let handler delete files when deleting upgrade

* Add mechanism for user to bulk-change status for purchase credits

* Tweak how pyramid config is created during app startup, for tests

* Fix permission used for mobile receiving item lookup


0.6.31 (2017-08-13)
-------------------

* Add show all vs. show diffs for upgrade packages

* Add initial support for changelog links for upgrade package diffs

* Add prev/next buttons when viewing upgrade details

* Merge 'better' theme into base templates


0.6.30 (2017-08-12)
-------------------

* Make product field renderer allow override of link text rendering


0.6.29 (2017-08-11)
-------------------

* Various tweaks to inventory batch logic (zero-all mode etc.)

* Fix join bug for users grid

* Flush session once every 1000 records when bulk-deleting


0.6.28 (2017-08-09)
-------------------

* Fix clone config bug for label batches


0.6.27 (2017-08-09)
-------------------

* Improve inventory support, plus "hiding" person data while still using it

* Fix encoding bug when reading stdout during upgrade


0.6.26 (2017-08-09)
-------------------

* Add awareness of upgrade exit code, success/fail

* Add support for cloning an upgrade record

* Add running display of stdout.log when executing upgrade


0.6.25 (2017-08-08)
-------------------

* Specify ``expire_on_commit`` for tailbone db session


0.6.24 (2017-08-08)
-------------------

* Fix bug which caused new empty worked shift when editing time sheet


0.6.23 (2017-08-08)
-------------------

* Fix bulk-delete for batch rows, allow it for pricing batches

* Fix permission check for deleting single batch rows

* Fix numeric filter to allow 3 decimal places by default


0.6.22 (2017-08-08)
-------------------

* Remove unwanted import (which broke versioning)

* Add some links to employees grid


0.6.21 (2017-08-08)
-------------------

* Refactor progress bars somewhat to allow file-based sessions

* Fix recipients renderer for email settings grid

* Improve status tracking for upgrades; add package version diff


0.6.20 (2017-08-07)
-------------------

* Record become/stop root user events

* Make datasync changes bulk-deletable

* Add basic support for performing / tracking app upgrades


0.6.19 (2017-08-04)
-------------------

* Record basic user login/logout events

* Expose UserEvent table in UI


0.6.18 (2017-08-04)
-------------------

* Add progress support for bulk deletion

* Make tempmon readings bulk-deletable


0.6.17 (2017-08-04)
-------------------

* Various view tweaks


0.6.16 (2017-08-04)
-------------------

* Add auto-links for most grids

* Fix row highlighting for sources panel on product view


0.6.15 (2017-08-03)
-------------------

* Allow product field renderer to suppress hyperlink

* Add 'data-uuid' attr for mobile grid list items, if applicable

* Initial (partial) support for mobile ordering

* Some tweaks to ordering batch views

* Fix bug when request.user becomes unattached from session (?)

* Add view for consuming new batch ID

* Add some links to various grid columns

* Fix bug in master view_row


0.6.14 (2017-08-01)
-------------------

* Make login template use same logo as home page

* Fix how we detect grid settings presence in user session

* Improve verbiage for exception view

* Fix styles for message compose template

* Various improvements to batch worksheets, index links etc.

* Fix batch links when viewing purchase object

* Add "on order" count to products grid, tweak product notes panel


0.6.13 (2017-07-26)
------------------

* Allow master view to decide whether each grid checkbox is checked


0.6.12 (2017-07-26)
------------------

* Add basic support for product inventory and status

* Stop allowing pre-0.7 SQLAlchemy


0.6.11 (2017-07-18)
------------------

* Tweak some basic styles for forms/grids

* Add new v3 master with v2 forms, with colander/deform


0.6.10 (2017-07-18)
------------------

* Fix grid bug if "current page" becomes invalid


0.6.9 (2017-07-15)
------------------

* Expose version history for all supported tables


0.6.8 (2017-07-14)
------------------

* Provide default renderers for SA mapped tables, where possible

* Add flexible grid class for v3 grids for width=half etc.

* Final grid refactor; we now have just 'grids' :)

* Refactor (coalesce) all batch-related templates


0.6.7 (2017-07-14)
------------------

* Fix master view ``get_effective_data()`` for v3 grids


0.6.6 (2017-07-14)
------------------

* Fix bug for printing one-off product labels


0.6.5 (2017-07-14)
------------------

* Fix template/styles for v3 grid views, add purchasing batch status


0.6.4 (2017-07-14)
------------------

* Add new "v3" grids, refactor all views to use them


0.6.3 (2017-07-13)
------------------

* Sort mobile receiving batches by ID desc

* Add initial/basic support for "simple" mobile grid filter w/ radio buttons

* Add filter support for mobile row grid; plus mark receiving as complete

* Disable unused Clear button for mobile receiving

* Add logic for mobile receiving if product not in batch and/or system

* Prevent mobile receiving actions for batch which is complete or executed

* Fix bug with mobile receiving UPC lookup; require stronger "create row" perm

* Stop using popup for expiration date, for mobile receiving

* Add global key handler for mobile receiving, for scanner wedge input

* Make all batches support mobile by default

* Add basic support for viewing inventory batches on mobile

* Refactor keypad widget for mobile receiving

* Add unit cost for inventory batches


0.6.2 (2017-07-10)
------------------

* Fix CS/EA bug for mobile receiving


0.6.1 (2017-07-07)
------------------

* Switch license to GPL v3 (no longer Affero)

* Fix broken product image tag, per webhelpers2


0.6.0 (2017-07-06)
------------------

Main reason for bumping version is the (re-)addition of data versioning support
using SQLAlchemy-Continuum.  This feature has been a long time coming and while
not yet fully implemented, we have a significant head start.

* Add custom default grid row size for Trainwreck items

* Make hyperlink optional for employee field renderer

* Tweak how customer/person relationships are displayed

* Add initial support for expiration date for mobile receiving

* Make Person.employee field readonly

* Rearrange some imports to ensure ``rattail.db.model`` comes last

* Add basic versioning history support for master view

* Remove old-style continuum version views

* Remove all "old-style" (aka. version 1) grids

* Remove all old-style views: grids, CRUD, versions etc.

* Refactor to use webhelpers2 etc. instead of older 'webhelpers'


0.5.104 (2017-06-22)
--------------------

* Add basic views for Trainwreck transactions

* Add ``AlchemyLocalDateTimeFilter``

* Add row count as available column to batch header grids

* Try to keep batch status updated; display it for handheld batches

* Tweak display of inventory/label batches to reflect multiple handheld batches

* Add way to execute multiple handheld batches (search results) at once

* Fix batch row count when deleting a row

* Make case/unit quantities prettier within Inventory batch rows grid

* Sort (alphabetically) device type list field when making new handheld batch

* Allow bulk row deletion for vendor catalog batches


0.5.103 (2017-06-05)
--------------------

* Always add key as class to grid column headers; allow literal label


0.5.102 (2017-05-30)
--------------------

* Remove all views etc. for old-style batches

* Fix bug when updating Order Form data, if row.po_total is None


0.5.101 (2017-05-25)
--------------------

* Fix subtle bug when identifying purchase batch row on order form update

* Remove references to deprecated batch handler methods

* Add validation for unique name when creating new Setting

* Simplify page title display for mobile base template

* Refactor "purchasing" batch views, split off "ordering"

* Add initial (full-ish) support for mobile receiving views

* Add support for bulk-delete of Pricing Batches

* Pad session timeout warning by 10 seconds, to account for drift

* Add highlight to active row within Order Form view

* Make 'notes' field use textarea renderer by default, for all batches

* Add basic ability to download Ordering Batch as Excel spreadsheet


0.5.100 (2017-05-18)
--------------------

* Allow batch view to override execution failure message

* Tweak some customer view/field rendering, to allow more customization

* Remove customer view template (use master default)

* Add basic support for Trainwreck database connectivity

* Remove unused 'fake_error' view

* Add basic 'robots.txt' support to CommonView

* Cap our pyramid_tm version until we can upgrade to pyramid 1.9

* Add daily hour totals when viewing or editing single employee time sheet

* Let config cause time sheet hours to display as HH.HH for some users

* Expose full-time flag and start date for employee view

* Add convenience ``dialog_button()`` JS function


0.5.99 (2017-05-05)
-------------------

* Add allowance for Escape key, in numeric.js

* Let a batch disallow bulk-deletion of its rows

* Add basic support for deletion speedbump for row data

* Remove lower version for Pyramid dependency, but restrict to pre-1.9


0.5.98 (2017-04-18)
-------------------

* Auto-save time sheet day editor on Enter press if time field is focused

* Add simple flag to prevent multiple submits for Order Form AJAX


0.5.97 (2017-04-04)
-------------------

* Fix signature for ``MasterView.get_index_url()``


0.5.96 (2017-04-04)
-------------------

* Tweak logic for registering exception view, to avoid test breakage

* Add basic paging grid/index support for mobile

* Tweak field label styles for mobile

* Allow config to define home page image URL


0.5.95 (2017-03-29)
-------------------

* Tweak organization panel for product view template

* Add logic to core View class, to force logout if user becomes inactive

* Detect "backwards" shift when time sheet is edited, alert user

* Add default view for unhandled exceptions, configure only for production

* Add basic table listing view, with rough estimate row counts

* Add 'status' column to vendor cost table in product view

* Various template standardization tweaks


0.5.94 (2017-03-25)
-------------------

* Add ``CostFieldRenderer`` and tweak product view template

* Bump margin between grid and header table, i.e. buttons

* Broad refactor to improve customization of purchase order form etc.

* Fix route sequence for people autocomplete

* Fix bugs when checking for 'chuck' in demo mode

* Add unit item and pack size fields to product view


0.5.93 (2017-03-22)
-------------------

* Add 'is_any' verb to integer grid filters

* Add more variations of project name when creating via scaffold

* Various tweaks to the customer and person views/forms

* Add basic "mobile index" master view, plus support for demo mode

* Refactor the batch file field renderer somewhat

* Move ``notfound()`` method to core ``View`` class

* Add ``BatchMasterView.add_file_field()`` convenience method

* Add ``extra_main_fields()`` method to product view template

* Allow config to override jQuery UI version

* Add master view for Report Output data model


0.5.92 (2017-03-14)
-------------------

* Tweak grid configuration for Employees view

* Add trailing '?' for employee time sheet when hours are incomplete


0.5.91 (2017-03-03)
-------------------

* Add 'discontinued' flag to product view


0.5.90 (2017-03-01)
-------------------

* Add notes, ingredients to product view


0.5.89 (2017-02-24)
-------------------

* Expose/honor per-role session timeouts

* Fix daylight savings bug when cloning schedule from previous week

* Expose notes field for purchasing batches

* Add some product flags (kosher vegan etc.) to view fieldset

* Add initial support for native product images


0.5.88 (2017-02-21)
-------------------

* Fix session reference bug in schedule view


0.5.87 (2017-02-21)
-------------------

* Fix bug in DateFieldRenderer when no format specified


0.5.86 (2017-02-21)
-------------------

* Add initial/basic views for customer orders data

* Be less aggressive when validating schedule edit form POST


0.5.85 (2017-02-19)
-------------------

* Add generic "bulk delete" support to MasterView

* Add beginnings of mobile receiving views


0.5.84 (2017-02-17)
-------------------

* Tweak progress template to better handle reset to 0%

* Add ability to merge 2 user accounts

* Increase size of Roles select when editing a User

* Add ability to filter Sent Messages by recipient name


0.5.83 (2017-02-16)
-------------------

* Set form id for new purchasing batch page

* Make sure invoice number is saved when making new purchasing batch

* Tweak product view page styles (new grids etc.)

* Add support for client-side session timeout warning


0.5.82 (2017-02-14)
-------------------

* Collapse grid actions if there are only 2

* Add master view for generic exports

* Make some product fields readonly

* Make datasync changes viewable

* Redirect to login page when Forbidden happens with anonymous user

* Tweak styles for Send Message page

* Tweak form handling for sending a new message, for more customization

* Advance to password field when Enter pressed on username, login page

* Add way for ``login_user()`` to set different timeout depending on nature of login


0.5.81 (2017-02-11)
-------------------

* Add config for redirecting user to home page after logout

* Refactor logic used to login a user, for easier sharing

* Use ``pretty_hours()`` function where applicable


0.5.80 (2017-02-10)
-------------------

* Tweak renderer for Amount field for DepositLink view

* Tweak how regular/current price fields are handled for Product view

* Fix bug in base 'shifts' template if ``weekdays`` not in context


0.5.79 (2017-02-09)
-------------------

* Tweak product view template per rename of case_size field

* Refactor the Edit Time Sheet view for "autocommit" mode

* Don't render user field as hyperlink unless so configured

* Expose 'delay' field in tempmon client views

* Fix bug when first entry is empty for product on ordering form


0.5.78 (2017-02-08)
-------------------

* Add initial Find Roles/Users by Permission feature

* Fix sorting bug for Employee Time Sheet view


0.5.77 (2017-02-04)
-------------------

* Invoke timepicker to correct format of user input, for edit schedule/timesheet


0.5.76 (2017-02-04)
-------------------

* Add hyperlink to ``EmployeeFieldRenderer``

* Improve the grid for ``WorkedShift`` model a bit

* Add config flag for disabling option to "Clear Schedule"


0.5.75 (2017-02-03)
-------------------

* Fix probe filter for tempmon readings grid

* Be explicit about fieldset for pricing batch rows

* Let project override user authentication for login page

* Add basic support for per-user session timeout


0.5.74 (2017-01-31)
-------------------

* Refactor schedule / timesheet views for better separation of concerns


0.5.73 (2017-01-30)
-------------------

* Add pyramid_mako dependency, remove minimum version for rattail

* Add ability to edit employee time sheet

* Add 'target' kwarg for grid action links

* Add hyperlink to User field renderer

* Add min diff threshold param when making price batch from product query

* Add way for batch views to hide rows with given status code(s)


0.5.72 (2017-01-29)
-------------------

* Add basic support for cloning batches

* Tweaks to order form template etc., for purchasing batch

* Let master view with rows prevent sort/filter for row grid

* Add price diff column to pricing batch row grid

* Add warning highlight for pricing batch row if can't calculate price


0.5.71 (2017-01-24)
-------------------

* Improve columns, filters for TempMon Readings grid

* Add ability to merge subdepartments


0.5.70 (2017-01-11)
-------------------

* Fix CSRF token bug with email preview form, refactor to use webhelpers


0.5.69 (2017-01-06)
-------------------

* When making batch from products, build query *before* starting thread


0.5.68 (2017-01-03)
-------------------

* Prefer received quantities over ordered quantities, for Order Form history


0.5.67 (2017-01-03)
-------------------

* Add department UUID to JSON returned for "eligible purchases" when creating batch

* Set "order date" when creating new receiving batch

* Add "discarded" flag when receiving DMG/EXP products; add view for purchase credits

* Fix type error in grid numeric filter


0.5.66 (2016-12-30)
-------------------

* Tweak the "create" screen for purchase batches, for more customization


0.5.65 (2016-12-29)
-------------------

* Fix purchase batch execution, to redirect to Purchase *or* Batch

* Add extra perms for restricing which 'mode' of purchase batch user can create

* Refactor Order Form a bit to allow custom history data


0.5.64 (2016-12-28)
-------------------

* Tweak default "numeric" grid filter, to ignore UPC-like values

* Tweak default filter label for Batch ID


0.5.63 (2016-12-28)
-------------------

* Fix CSRF token bug for bulk-move message forms


0.5.62 (2016-12-22)
-------------------

* Fix CSRF token bug for old-style batch params form


0.5.61 (2016-12-21)
-------------------

* Fix master merge template/forms to include CSRF token


0.5.60 (2016-12-20)
-------------------

* Fix CSRF bug in Ordering Form template, make case quantity pretty

* Fix some bugs in product view template

* Update some enum references, render all purchase/batch cases/units fields as quantity


0.5.59 (2016-12-19)
-------------------

* Add ``QuantityFieldRenderer``

* Add style for 'half-width' grid


0.5.58 (2016-12-16)
-------------------

* Add ``ValidGPC`` formencode validator

* Overhaul the Receiving Form to account for "product not found" etc.

* Auto-append slash to URL when necessary

* Add "print receiving worksheet" feature, for 'ordered' purchases

* Add global CSRF protection

* Tweak some field renderers

* Overhaul product views a little, per customization needs


0.5.57 (2016-12-12)
-------------------

* Lots of changes for sake of mobile login / user menu etc.

* Add mobile support for datasync restart

* Make ``CurrencyFieldRenderer`` inherit from ``FloatFieldRenderer``

* Fix session bug in old CRUD views


0.5.56 (2016-12-11)
-------------------

* Show 'enabled' column in grid, fix prefix bug for email profiles

* Tweak flash message when sending email preview, in case it's disabled

* Hide first/last name for employee view, unless in readonly mode

* Add initial mobile templates: base, home, about


0.5.55 (2016-12-10)
-------------------

* Validate for unique tempmon probe config key

* Add 'restartable tempmon client' conditional logic


0.5.54 (2016-12-10)
-------------------

* Add new 'receiving form' for purchase batches

* Add support for 'department' field in purchases / batches

* Add generic 'not on file' product image for use as POD 404

* Add logic for handling Ctrl+V / Ctrl+X in numeric.js


0.5.53 (2016-12-09)
-------------------

* Fix bug when editing a data row


0.5.52 (2016-12-08)
-------------------

* Fix permission group label for email bounces

* Update footer text/link per new about page


0.5.51 (2016-12-07)
-------------------

* Fix permission / grid action bug for email profiles


0.5.50 (2016-12-07)
-------------------

* Tweak tempmon views a little, fix client restart logic

* Add 'extra_styles' to true base template

* Add new "bytestring" filter for grids that need it


0.5.49 (2016-12-05)
-------------------

* Allow delete for datasync changes

* Fix import bugs with tempmon views

* Use master view's session when creating form


0.5.48 (2016-12-05)
-------------------

* Tweak email config views, to support subject "templates"

* Refactor tempmon views to leverage rattail-tempmon database


0.5.47 (2016-11-30)
-------------------

* Fix bug in products view class


0.5.46 (2016-11-29)
-------------------

* Add basic 'about' page with some package versions

* Tweak fields for product view


0.5.45 (2016-11-28)
-------------------

* Fix styles for 'print schedule' page

* Add permission for bulk-delete of batch data rows


0.5.44 (2016-11-22)
-------------------

* Add some links between employees / people / customers views

* Add support for pricing batches

* Add initial views for tempmon clients/probes/readings


0.5.43 (2016-11-21)
-------------------

* Add support for receive/cost mode, purchase relation for purchase batches

* Bump jquery version

* Fix bug when downloading batch file


0.5.42 (2016-11-20)
-------------------

* Move ``get_batch_kwargs()`` to ``BatchMasterView``


0.5.41 (2016-11-20)
-------------------

* Add printer-friendly view for "full" employee schedule

* Fix some bugs etc. with batch views and templates


0.5.40 (2016-11-19)
-------------------

* Add size, extra link fields to product view template

* Refactor batch views / templates per rattail framework overhaul


0.5.39 (2016-11-14)
-------------------

* Make POD image for product view a bit more sane

* Disable save button when creating new object


0.5.38 (2016-11-11)
-------------------

* Tweak default factory for boolean grid filters

* Add support for more cases + units, more vendor fields, for new purchase batches


0.5.37 (2016-11-10)
-------------------

* Display sequence for product alt codes

* Change how we determine default 'grid key' for master views

* Add 'additive fields' concept to merge diff preview


0.5.36 (2016-11-09)
-------------------

* Add historical amounts to new purchase Order Form, allow extra columns etc.

* Tweak verbiage for merge template etc.


0.5.35 (2016-11-08)
-------------------

* Add support for new Purchase/Batch views, 'create row' master pattern

* Add basic views for label batches

* Add support for making new-style batches from products grid query

* Add initial support for viewing new purchase batch as Order Form

* Refactor how batch editing is done; don't include rows for that sometimes


0.5.34 (2016-11-02)
-------------------

* Add basic merge feature to ``MasterView``


0.5.33 (2016-10-27)
-------------------

* Fix template bug when deleting user

* Tweak default styles for home page

* Show vendor invoice rows as warning, if they have no case quantity

* Add 'vendor code' and 'vendor code (any)' filters for products grid

* Fix bug with how we auto-filter 'deleted' products (?)


0.5.32 (2016-10-19)
-------------------

* Fix / improve progress display somewhat

* Disable "true delete" button by default, when clicked

* Fix bug in batch ID field renderer, when displayed for new batch

* Add ``refresh_after_create`` flag for ``BatchMasterView``

* Disable a focus() call in menubar.js which messed with search filter focus

* Let any 'admin' user elevate to 'root' for full system access

* Update references to ``request.authenticated_userid``


0.5.31 (2016-10-14)
-------------------

* Add ability to edit employee schedule


0.5.30 (2016-10-10)
-------------------

* Tweak some things to make demo project more "out of the box"

* Add registration for 'rattail' template with Pyramid scaffold system

* Add 'tailbone' to global template context, update 'better' template footer

* Tweak how tailbone finds rattail config from pyramid settings

* Remove last references to 'edbob' package

* Strip whitespace from username field when editing User

* Fix couple of bugs for vendor catalog views

* Add size description to inventory report


0.5.29 (2016-10-04)
-------------------

* Add ``code`` field to Category views

* Add "bulk delete rows" feature to new batches view


0.5.28 (2016-09-30)
-------------------

* Add specific permissions for edit/delete of individual batch rows


0.5.27 (2016-09-26)
-------------------

* Add basic form validation when sending new messages

* Add "just in time" editable instance check for master view

* Add "refresh" button when viewing batch

* Add FormAlchemy-compatible validators for email address, phone number

* Improve validation for FormAlchemy date field renderer

* Fix row-level visibility for grid edit action

* Add a couple of extra verbs to base grid filter class

* Tweak how a grid filter factory is determined


0.5.26 (2016-09-01)
-------------------

* Add ``MasterView.listable`` flag for disabling grid view

* Fix permission group label bug for batch views

* Allow opt-out for "download batch row data as CSV" feature


0.5.25 (2016-08-23)
-------------------

* Tweak how we use DB session to fetch grid settings

* Add "sub-rows" support to MasterView class

* Refactor batch views to leverage MasterView sub-rows logic

* Refactor batch view/edit pages to share some "execution options" logic

* Add hook to customize timesheet shift rendering


0.5.24 (2016-08-17)
-------------------

* Fix bug in handheld batch view config


0.5.23 (2016-08-17)
-------------------

* Fix bug when viewing batch with no execution options


0.5.22 (2016-08-17)
-------------------

* Fix bug for handheld batch device type field


0.5.21 (2016-08-17)
-------------------

* Add ``MasterView.render()`` method for sake of common context/logic

* Add "empty" option to enum field renderers, if field allows empty value

* Add support for system-unique ID in batch views etc.

* Fix bug when deleting certain batches

* Fix bug in batch download URL

* Add basic support for batch execution options

* Add basic support for new handheld/inventory batches


0.5.20 (2016-08-13)
-------------------

* Add null / not null verbs back to default boolean grid filter


0.5.19 (2016-08-12)
-------------------

* Only show granted permissions when viewing role details

* Expose 'enabled' flag for email profile/settings

* Add permissions field when viewing user details


0.5.18 (2016-08-10)
-------------------

* Add ``render_progress()`` method to core view class

* Add hopefully generic ``FileFieldRenderer``


0.5.17 (2016-08-09)
-------------------

* Add support for 10-key hyphen/period keys for numeric input fields


0.5.16 (2016-08-05)
-------------------

* Fallback to empty string for email preview recipient, if current user has no address

* Allow negative sign, decimal point for "numeric" text fields


0.5.15 (2016-07-27)
-------------------

* Add initial attempt at 'better' theme

* Add ``CodeTextAreaFieldRenderer``, refactor label profile form to use it


0.5.14 (2016-07-08)
-------------------

* Allow extra kwargs to core ``View.redirect()`` method

* Add awareness of special 'Authenticated' role, in permissions UI etc.

* Always strip whitespace from label profile 'spec' field input


0.5.13 (2016-06-10)
-------------------

* Hopefully fix some CSS for form field values

* Add support for viewing single employee's schedule / time sheet


0.5.12 (2016-05-11)
-------------------

* Add support for "full" schedule and time sheet views.

* Move "full name" to front of Person grid columns.

* Add rattail config object to ``Session`` kwargs.


0.5.11 (2016-05-06)
-------------------

* Refactor some common FormEncode validators, plus add some more.

* Tweak styles for jQuery UI selectmenu dropdowns.

* Tweak timesheet styles, to give rows alternating background color.

* Disable autocomplete for password fields when editing user.

* Various incomplete improvements to the timesheet/schedule views.


0.5.10 (2016-05-05)
-------------------

* Refactor timesheet logic, add basic schedule view.

* Add prev/next/jump week navigation to time sheet, schedule views.

* Add hyperlinks to product UPC and description, within main grid.

* Fix bug in roles view.


0.5.9 (2016-05-02)
------------------

* Remove 'create batch from results' link on products index page.

* Fix bugs in batch grid URLs.

* Tweak how empty hours are displayed in time sheet.


0.5.8 (2016-05-02)
------------------

* Add ``MasterView.listing`` flag, for templates' sake.

* Overhaul newgrid template header a bit, to improve styles.

* Move ``Person.display_name`` to top of fieldset when viewing/editing.

* Add 'testing' image, for background / watermark.

* Add 'index title' setting to master view.

* Add auto-hide/show magic to message recipients field when viewing.

* Add initial support for grid index URLs.

* Add initial/basic user feedback form support.

* Stop trying to use PIL when generating product image tag.


0.5.7 (2016-04-28)
------------------

* Add master views for ``ScheduledShift`` model.

* Add initial (incomplete) Time Sheet view.


0.5.6 (2016-04-25)
------------------

* Add views for ``WorkedShift`` model.


0.5.5 (2016-04-24)
------------------

* Add workarounds for certain display bugs when rendering datetimes.

* Make currency field renderer display negative amounts in parentheses.

* Add commas to record/page count in grid footer.

* Tweak styles for form field labels.


0.5.4 (2016-04-12)
------------------

* Add support for column header title (tooltip) in new grids.

* Change default filter type for integer fields, in new grids.

* Add flag for rendering key value, for enum field renderers.

* Fix case-sensitivity when sorting permission group labels.


0.5.3 (2016-04-05)
------------------

* Fix redirect bug when attempting bulk row delete for nonexistent batch.

* Add comma magic back to ``CurrencyFieldRenderer``.

* Add the 'is any' verb to default list for most grid filters.

* Add new ``TimeFieldRenderer``, make it default for ``Time`` fields.

* Add last-minute check to ensure master views allows deletion.


0.5.2 (2016-03-11)
------------------

* Make ``tailbone.views.labels`` a subpackage instead of module.

* Add 'executed' to old batches grid view.

* Make all timestamps show "raw" by default (with "diff" tooltip).

* Improve grid filters for datetime fields (smarter verbs).

* Fix bug where batch creator was being set to current user anytime it was viewed..yikes.


0.5.1 (2016-02-27)
------------------

* Fix bug when rendering email bounce links.


0.5.0 (2016-02-15)
------------------

* Refactor products view(s) per new master pattern.

* Make our ``DateTimeFieldRenderer`` the default for datetime fields.

* Add new ``BatchMasterView`` for new-style batches.

* Overhaul vendor catalogs, vendor invoices views to use new batch master class.

* Refactor some more model views to use MasterView. (depositlink, tax, emailbounce)

* Make datasync views easier to customize.


0.4.42
------

* Add initial reply / reply-all support for messages.

* Add subscriber hook for setting inbox count in template context.


0.4.41
------

* Tweak how we connect a user to a batch, when refreshing.

* Add 'Move' button to message view template.


0.4.40
------

* Make rattail config object use our scoped session, when consulting db.


0.4.39
------

* Add support for sending new messages.


0.4.38
------

* Add 'password is/not null' filter to users list view.

* Remove style hack for message grid views.


0.4.37
------

* Add 'messages.list' permission, to protect inbox etc.


0.4.36
------

* Fix bug when marking batch as executed.


0.4.35
------

* Change default form buttons so Cancel is also a button.

* Add 'Stores' and 'Departments' fields to Employee fieldset.


0.4.34
------

* Add 'restart datasync' button to datasync changes list page.

* Add autocomplete vendor field renderer.

* Change vendor catalog upload, to allow vendor-less parsers.

* Stop depending on PIL...for now?


0.4.33
------

* Add employee/department relationships to employee and department views.


0.4.32
------

* Add edit mode for email "profile" settings.

* Fix auto-creation of grid sorter, when joined table is involved.

* Add initial support for 'messages' views.


0.4.31
------

* Add speed bump / confirmation page when deleting records.

* Add "grid tools" to "complete" grid template.

* Add ``Person.middle_name`` to the fieldset.


0.4.30
------

* Add config extension, to record data changes if so configured.

* Add mailing address to person fieldset.


0.4.29
------

* Fix some route names.


0.4.28
------

* Use sample data when generating subject for display in email profile settings.

* Convert (most?) basic views to use master view pattern.


0.4.27
------

* Change default sortkey for email profiles list.

* Add 'To' field to email profile settings grid.


0.4.26
------

* Add readonly support for email profile settings.


0.4.25
------

* Fix bug when 'edbob.permissions' setting is empty.

* Tweak some things to get Tailbone working on its own.

* Let subclass of MasterView override the database Session it uses.


0.4.24
------

* Render ``DataSyncChange.obtained`` as humanized timestamp within UI.


0.4.23
------

* Delete product costs for vendor when deleting vendor.

* Work around formalchemy config bug, caused by edbob.

* Add view to show DataSync changes, for basic troubleshooting.


0.4.22
------

* Remove format hack which isn't py2.6-friendly.


0.4.21
------

* Add "valueless verbs" concept to grid filters.

* Tweak labels for new grid filter form buttons.

* Configure logging when starting up.

* Add HTML5 doctype to base template.

* More grid filter improvements; add choice/enum/date value renderers.

* Treat filter by "contains X Y" as "contains X and contains Y".

* Tweak layout CSS so page body expands to fill screen.


0.4.20
------

* Add ``CurrencyFieldRenderer``.

* Add basic checkbox support to new grids.

* Add 'Default Filters' and 'Clear Filters' buttons to new grid filters form.

* Add "Save Defaults" button so user can save personal defaults for any new grid.

* Fix bug when rendering hidden field in FA fieldset.

* Remove some unused styles.

* Various tweaks to support "late login" idea when uploading new batch.

* Hard-code old grid pagecount settings, to avoid ``edbob.config``.

* Refactor app configuration to use ``rattail.config.make_config()``.

* Tweak label formatter instantiation, per rattail changes.

* Various tweaks to base batch views.

* Add ``CustomFieldRenderer`` and ``DateFieldRenderer``.

* Add ``configure_fieldset()`` stub for master view.

* Add progress indicator to batch execution.

* Add ability to download batch row data as CSV.


0.4.19
------

* Fix progress template, per jQuery CDN changes.


0.4.18
------

* Don't show flash message when user logs in.

* Add core JS/CSS to base template; use CDN instead of cached files.

* Add support for "new-style grids" and "model master views", and convert the
  following views to use it: roles, users, label profiles, settings.  Also
  overhaul how permissions are registered in app config.


0.4.17
------

* Log warning instead of error when refreshing batch fails.


0.4.16
------

* Add initial support for email bounce management.


0.4.15
------

* Fix missing import bug.


0.4.14
------

* Make anchor tags with 'button' class render as jQuery UI buttons.

* Tweak ``app.make_rattail_config()`` to allow caller to define some settings.

* Add ``display_name`` field to employee CRUD view.

* Allow batch handler to disable the Execute button.

* Add ``StoreFieldRenderer`` and ``DecimalFieldRenderer``.

* Tweak how default filter config is handled for batch grid views.

* Add list of assigned users to role view page.

* Add products autocomplete view.

* Add ``rattail_config`` attribute to base ``View`` class.

* Fix timezone issues with ``util.pretty_datetime()`` function.

* Add some custom FormEncode validators.


0.4.13
------

* Fix query bugs for batch row grid views (add join support).

* Make vendor field renderer show ID in readonly mode.

* Change permission requirement for refreshing a batch's data.

* Add flash message when any batch executes successfully.

* Add autocomplete view for current employees.

* Add autocomplete employee field renderer.

* Fix usage of ``Product.unit_of_measure`` vs. ``Product.weighed``.


0.4.12
------

* Fix bug when creating batch from product query.


0.4.11
------

* Tweak old-style batch execution call.


0.4.10
------

* Add 'fake_error' view to test exception handling.

* Add ability to view details (i.e. all fields) of a batch row.

* Fix bulk delete of batch rows, to set 'removed' flag instead.

* Fix vendor invoice validation bug.

* Add dept. number and friends to product details page.

* Add "extra panels" customization hook to product details template.


0.4.9
-----

* Hide "print labels" column on products list view if so configured.


0.4.8
-----

* Fix permission for deposit link list/search view.

* Fix permission for taxes list/search view.


0.4.7
-----

* Add views for deposit links, taxes; update product view.

* Add some new vendor and product fields.

* Add panels to product details view, etc.

* Fix login so user is sent to their target page after authentication.

* Don't allow edit of vendor and effective date in catalog batches.

* Add shared GPC search filter, use it for product batch rows.

* Add default ``Grid.iter_rows()`` implementation.

* Add "save" icon and grid column style.

* Add ``numeric.js`` script for numeric-only text inputs.

* Add product UPC to JSON output of 'products.search' view.


0.4.6
-----

* Add vendor catalog batch importer.

* Add vendor invoice batch importer.

* Improve data file handling for file batches.

* Add download feature for file batches.

* Add better error handling when batch refresh fails, etc.

* Add some docs for new batch system.

* Refactor ``app`` module to promote code sharing.

* Force grid table background to white.

* Exclude 'deleted' items from reports.

* Hide deleted field from product details, according to permissions.

* Fix embedded grid URL query string bug.


0.4.5
-----

* Add prettier UPCs to ordering worksheet report.

* Add case pack field to product CRUD form.


0.4.4
-----

* Add UI support for ``Product.deleted`` column.


0.4.3
-----

* More versioning support fixes, to allow on or off.


0.4.2
-----

* Rework versioning support to allow it to be on or off.


0.4.1
-----

* Only attempt to count versions for versioned models (CRUD views).


0.4.0
-----

This version primarily got the bump it did because of the addition of support
for SQLAlchemy-Continuum versioning.  There were several other minor changes as
well.

* Add department to field lists for category views.

* Change default sort for People grid view.

* Add category to product CRUD view.

* Add initial versioning support with SQLAlchemy-Continuum.


0.3.28
------

* Add unique username check when creating users.

* Improve UPC search for rows within batches.

* New batch system...


0.3.27
------

* Fix bug with default search filters for SA grids.

* Fix bug in product search UPC filter.

* Ugh, add unwanted jQuery libs to progress template.

* Add support for integer search filters.


0.3.26
------

* Use boolean search filter for batch column filters of 'FLAG' type.


0.3.25
------

* Make product UPC search view strip non-digit chars from input.


0.3.24
------

* Make ``GPCFieldRenderer`` display check digit separate from main barcode
  data.

* Add ``DateTimeFieldRenderer`` to show human-friendly timestamps.

* Tweak CRUD form buttons a little.

* Add grid, CRUD views for ``Setting`` model.

* Update ``base.css`` with various things from other projects.

* Fix bug with progress template, when error occurs.


0.3.23
------

* Fix bugs when configuring database session within threads.


0.3.22
------

* Make ``Store.database_key`` field editable.

* Add explicit session config within batch threads.

* Remove cap on installed Pyramid version.

* Change session progress API.


0.3.21
------

* Add monospace font for label printer format command.


0.3.20
------

* Refactor some label printing stuff, per rattail changes.


0.3.19
------

* Add support for ``Product.not_for_sale`` flag.


0.3.18
------

* Add explicit file encoding to all Mako templates.

* Add "active" filter to users view; enable it by default.


0.3.17
------

* Add customer phone autocomplete and customer "info" AJAX view.

* Allow editing ``User.active`` field.

* Add Person autocomplete view which restricts to employees only.


0.3.16
------

* Add product report codes to the UI.


0.3.15
------

* Add experimental soundex filter support to the Customers grid.


0.3.14
------

* Add event hook for attaching Rattail ``config`` to new requests.

* Fix vendor filter/sort issues in products grid.

* Add ``Family`` and ``Product.family`` to the general grid/crud UI.

* Add POD image support to product view page.


0.3.13
------

* Use global ``Session`` from rattail (again).

* Apply zope transaction to global Tailbone Session class.


0.3.12
------

* Fix customer lookup bug in customer detail view.

* Add ``SessionProgress`` class, and ``progress`` views.


0.3.11
------

* Removed reliance on global ``rattail.db.Session`` class.


0.3.10
------

* Changed ``UserFieldRenderer`` to leverage ``User.display_name``.

* Refactored model imports, etc.
    
  This is in preparation for using database models only from ``rattail``
  (i.e. no ``edbob``).  Mostly the model and enum imports were affected.

* Removed references to ``edbob.enum``.


0.3.9
-----

* Added forbidden view.

* Fixed bug with ``request.has_any_perm()``.

* Made ``SortableAlchemyGridView`` default to full (100%) width.

* Refactored ``AutocompleteFieldRenderer``.
    
  Also improved some organization of renderers.

* Allow overriding form class/factory for CRUD views.

* Made ``EnumFieldRenderer`` a proper class.

* Don't sort values in ``EnumFieldRenderer``.
    
  The dictionaries used to supply enumeration values should be ``OrderedDict``
  instances if sorting is needed.

* Added ``Product.family`` to CRUD view.


0.3.8
-----

* Fixed manifest (whoops).


0.3.7
-----

* Added some autocomplete Javascript magic.
    
  Not sure how this got missed the first time around.

* Added ``products.search`` route/view.
    
  This is for simple AJAX uses.

* Fixed grid join map bug.


0.3.6
-----

* Fixed change password template/form.


0.3.5
-----

* Added ``forms.alchemy`` module and changed CRUD view to use it.

* Added progress template.


0.3.4
-----

* Changed vendor filter in product search to find "any vendor".
    
  I.e. the current filter is *not* restricted to the preferred vendor only.
  Probably should still add one (back) for preferred only as well; hence the
  commented code.


0.3.3
-----

* Major overhaul for standalone operation.
    
  This removes some of the ``edbob`` reliance, as well as borrowing some
  templates and styling etc. from Dtail.

  Stop using ``edbob.db.engine``, stop using all edbob templates, etc.

* Fix authorization policy bug.
    
  This was really an edge case, but in any event the problem would occur when a
  user was logged in, and then that user account was deleted.

* Added ``global_title()`` to base template.

* Made logo more easily customizable in login template.


0.3.2
-----

* Rebranded to Tailbone.


0.3.1
-----

* Added some tests.

* Added ``helpers`` module.
    
  Also added a Pyramid subscriber hook to add the module to the template
  renderer context with a key of ``h``.  This is nothing really new, but it
  overrides the helper provided by ``edbob``, and adds a ``pretty_date()``
  function (which maybe isn't a good idea anyway..?).

* Added ``simpleform`` wildcard import to ``forms`` module.

* Added autocomplete view and template.

* Fixed customer group deletion.
    
  Now any customer associations are dropped first, to avoid database integrity
  errors.

* Stole grids and grid-based views from ``edbob``.

* Removed several references to ``edbob``.

* Replaced ``Grid.clickable`` with ``.viewable``.
    
  Clickable grid rows seemed to be more irritating than useful.  Now a view
  icon is shown instead.

* Added style for grid checkbox cells.

* Fixed FormAlchemy table rendering when underlying session is not primary.
    
  This was needed for a grid based on a LOC SMS session.

* Added grid sort arrow images.

* Improved query modification logic in alchemy grid views.

* Overhauled report views to allow easier template customization.

* Improved product UPC search so check digit is optional.

* Fixed import issue with ``views.reports`` module.


0.3a23
------

* Fixed bugs where edit links were appearing for unprivileged users.

* Added support for product codes.
    
  These are shown when viewing a product, and may be used to locate a product
  via search filters.


0.3a22
------

* Removed ``setup.cfg`` file.

* Added ``Session`` to ``rattail.pyramid`` namespace.

* Added Email Address field to Vendor CRUD views.

* Added extra key lookups for customer and product routes.
    
  Now the CRUD routes for these objects can leverage UUIDs of various related
  objects in addition to the primary object.  More should be done with this,
  but at least we have a start.

* Replaced ``forms`` module with subpackage; added some initial goodies (many
  of which are currently just imports from ``edbob``).

* Added/edited various CRUD templates for consistency.

* Modified several view modules so their Pyramid configuration is more
  "extensible."  This just means routes and views are defined as two separate
  steps, so that derived applications may inherit the route definitions if they
  so choose.

* Added Employee CRUD views; added Email Address field to index view.

* Updated ``people`` view module so it no longer derives from that of
  ``edbob``.

* Added support for, and some implementations of, extra key lookup abilities to
  CRUD views.  This allows URLs to use a "natural" key (e.g. Customer ID
  instead of UUID), for cases where that is more helpful.

* Product CRUD now uses autocomplete for Brand field.  Also, price fields no
  longer appear within an editable fieldset.

* Within Store index view, default sort is now ID instead of Name.

* Added Contact and Phone Number fields to Vendor CRUD views; added Contact and
  Email Address fields to index view.
  

0.3a21
------

- [feature] Added CRUD view and template.

- [feature] Added ``AutocompleteView``.

- [feature] Added Person autocomplete view and User CRUD views.

- [feature] Added ``id`` and ``status`` fields to Employee grid view.


0.3a20
------

- [feature] Sorted the Ordering Worksheet by product brand, description.

0.3a19
------

- [feature] Made batch creation and execution threads aware of
  `sys.excepthook`.  Updated both instances to use `rattail.threads.Thread`
  instead of `threading.Thread`.  This way if an exception occurs within the
  thread, the registered handler will be invoked.

0.3a18
------

- [bug] Label profile editing now uses stripping field renderer to avoid
  problems with leading/trailing whitespace.

- [feature] Added Inventory Worksheet report.

0.3a17
------

- [feature] Added Brand and Size fields to the Ordering Worksheet.  Also
  tweaked the template styles slightly, and added the ability to override the
  template via config.

- [feature] Added "preferred only" option to Ordering Worksheet.

0.3a16
------

- [bug] Fixed bug where requesting deletion of non-existent batch row was
  redirecting to a non-existent route.

0.3a15
------

- [bug] Fixed batch grid and CRUD views so that the execution time shows a
  pretty (and local) display instead of 24-hour UTC time.

0.3a14
------

- [feature] Added some more CRUD.  Mostly this was for departments,
  subdepartments, brands and products.  This was rather ad-hoc and still is
  probably far from complete.

- [general] Changed main batch route.

- [bug] Fixed label profile templates so they properly handle a missing or
  invalid printer spec.

0.3a13
------

- [bug] Fixed bug which prevented UPC search from working on products screen.

0.3a12
------

- [general] Fixed namespace packages, per ``setuptools`` documentation.

- [feature] Added support for ``LabelProfile.visible``.  This field may now be
  edited, and it is honored when displaying the list of available profiles to
  be used for printing from the products page.

- [bug] Fixed bug where non-numeric data entered in the UPC search field on the
  products page was raising an error.

0.3a11
------

- [bug] Fixed product label printing to handle any uncaught exception, and
  report the error message to the end user.

0.3a10
------

- [general] Updated category views and templates.  These were sorely out of
  date.

0.3a9
-----

- Add brands autocomplete view.

- Add departments autocomplete view.

- Add ID filter to vendors grid.

0.3a8
-----

- Tweak batch progress indicators.

- Add "Executed" column, filter to batch grid.

0.3a7
-----

- Add ability to restrict batch providers via config.

0.3a6
-----

- Add Vendor CRUD.

- Add Brand views.

0.3a5
-----

- Added support for GPC data type.

- Added eager import of ``rattail.sil`` in ``before_render`` hook.

- Removed ``rattail.pyramid.util`` module.

- Added initial batch support: views, templates, creation from Product grid.

- Added support for ``rattail.LabelProfile`` class.

- Improved Product grid to include filter/sort on Vendor.

- Cleaned up dependencies.

- Added ``rattail.pyramid.includeme()``.

- Added ``CustomerGroup`` CRUD view (read only).

- Added hot links to ``Customer`` CRUD view.

- Added ``Store`` index, CRUD views.

- Updated ``rattail.pyramid.views.includeme()``.

- Added ``email_preference`` to ``Customer`` CRUD.

0.3a4
-----

- Update grid and CRUD views per changes in ``edbob``.

0.3a3
-----

- Add price field renderers.

- Add/tweak lots of views for database models.

- Add label printing to product list view.

- Add (some of) ``Product`` CRUD.

0.3a2
-----

- Refactor category views.

0.3a1
-----

-  Initial port to Rattail v0.3.
