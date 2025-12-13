# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request



class TravelAiController(http.Controller):

    def _get_website_company_env(self):
        """Return an env locked to the current website company."""
        company = request.website.company_id
        # Use core environment call because with_company/with_context are missing
        ctx = dict(request.env.context)
        ctx.update({
            "company_id": company.id,
            "allowed_company_ids": [company.id],
        })
        env = request.env(context=ctx)
        return env, company

    @http.route(
        "/travel/ai",
        type="http",
        auth="public",
        website=True,
        methods=["GET", "POST"],
        csrf=True,  # important
    )
    def travel_ai(self, **post):
        """
        PRG pattern:
        - POST creates log + processes -> redirect to /travel/ai?log_id=XX
        - GET renders either empty form or the log specified by log_id
        """
        env, company = self._get_website_company_env()

        # ---------- POST ----------
        if request.httprequest.method == "POST":
            question = (post.get("question") or "").strip()
            if not question:
                # Redirect with an error flag (simple, avoids stale POST resubmission)
                return request.redirect("/travel/ai?err=empty")

            # Create log in website company (sudo ok for logging, but company-bound)
            log = env["travel.ai.log"].sudo().create({
                "request_text": question,
                "company_id": company.id,
            })

            # Process recommendations (IMPORTANT: make the model code company-safe too)
            log.action_process()

            # Redirect to GET page showing that log
            return request.redirect("/travel/ai?log_id=%s" % log.id)

        # ---------- GET ----------
        err = (request.params.get("err") or "").strip()
        error_message = "Pertanyaan tidak boleh kosong." if err == "empty" else None

        log = None
        log_id = request.params.get("log_id")
        if log_id:
            try:
                log_id = int(log_id)
            except Exception:
                log_id = 0

            if log_id:
                # Only allow viewing logs belonging to this website company
                # (or adjust if you want shared logs)
                log = env["travel.ai.log"].sudo().browse(log_id)
                if not log.exists() or (log.company_id and log.company_id.id != company.id):
                    log = None

        values = {
            "log": log,
            "error_message": error_message,
        }
        return request.render("rc_travel_ai.travel_ai_page", values)

    @http.route(
        "/travel/ai/buy/<int:log_id>/<int:product_id>",
        type="http",
        auth="public",
        website=True,
        methods=["GET"],
    )
    def travel_ai_buy(self, log_id, product_id, **kw):
        """
        Store log_id in session, then redirect to product page.
        Enforce website company visibility (no cross-company buy).
        """
        env, company = self._get_website_company_env()

        # Validate log is same company
        log = env["travel.ai.log"].sudo().browse(log_id)
        if not log.exists() or (log.company_id and log.company_id.id != company.id):
            return request.redirect("/travel/ai")

        # Find product template in website company scope (no sudo, respect rules)
        product_tmpl = env["product.template"].browse(product_id)
        if not product_tmpl.exists():
            return request.redirect("/travel/ai?log_id=%s" % log_id)

        # Must be saleable and company-compatible: company_id False or website company
        if product_tmpl.company_id and product_tmpl.company_id.id != company.id:
            return request.redirect("/travel/ai?log_id=%s" % log_id)

        if not product_tmpl.sale_ok:
            return request.redirect("/travel/ai?log_id=%s" % log_id)

        # Store log in session so website_sale can attach it to the order
        request.session["rc_ai_log_id"] = log_id

        # Redirect to first variant product page (website_sale uses product.product route)
        variant = product_tmpl.product_variant_id
        return request.redirect("/shop/product/%s" % variant.id)



