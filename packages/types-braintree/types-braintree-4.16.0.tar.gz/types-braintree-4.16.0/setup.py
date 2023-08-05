from setuptools import setup

name = "types-braintree"
description = "Typing stubs for braintree"
long_description = '''
## Typing stubs for braintree

This is a PEP 561 type stub package for the `braintree` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `braintree`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/braintree. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `a70667804ace967eb8a6299b1429cde8b4bae4e5`.
'''.lstrip()

setup(name=name,
      version="4.16.0",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/braintree.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['braintree-stubs'],
      package_data={'braintree-stubs': ['__init__.pyi', 'account_updater_daily_report.pyi', 'ach_mandate.pyi', 'add_on.pyi', 'add_on_gateway.pyi', 'address.pyi', 'address_gateway.pyi', 'amex_express_checkout_card.pyi', 'android_pay_card.pyi', 'apple_pay_card.pyi', 'apple_pay_gateway.pyi', 'apple_pay_options.pyi', 'attribute_getter.pyi', 'authorization_adjustment.pyi', 'bin_data.pyi', 'braintree_gateway.pyi', 'client_token.pyi', 'client_token_gateway.pyi', 'configuration.pyi', 'connected_merchant_paypal_status_changed.pyi', 'connected_merchant_status_transitioned.pyi', 'credentials_parser.pyi', 'credit_card.pyi', 'credit_card_gateway.pyi', 'credit_card_verification.pyi', 'credit_card_verification_gateway.pyi', 'credit_card_verification_search.pyi', 'customer.pyi', 'customer_gateway.pyi', 'customer_search.pyi', 'descriptor.pyi', 'disbursement.pyi', 'disbursement_detail.pyi', 'discount.pyi', 'discount_gateway.pyi', 'dispute.pyi', 'dispute_details/__init__.pyi', 'dispute_details/evidence.pyi', 'dispute_details/paypal_message.pyi', 'dispute_details/status_history.pyi', 'dispute_gateway.pyi', 'dispute_search.pyi', 'document_upload.pyi', 'document_upload_gateway.pyi', 'environment.pyi', 'error_codes.pyi', 'error_result.pyi', 'errors.pyi', 'europe_bank_account.pyi', 'exceptions/__init__.pyi', 'exceptions/authentication_error.pyi', 'exceptions/authorization_error.pyi', 'exceptions/braintree_error.pyi', 'exceptions/configuration_error.pyi', 'exceptions/gateway_timeout_error.pyi', 'exceptions/http/__init__.pyi', 'exceptions/http/connection_error.pyi', 'exceptions/http/invalid_response_error.pyi', 'exceptions/http/timeout_error.pyi', 'exceptions/invalid_challenge_error.pyi', 'exceptions/invalid_signature_error.pyi', 'exceptions/not_found_error.pyi', 'exceptions/request_timeout_error.pyi', 'exceptions/server_error.pyi', 'exceptions/service_unavailable_error.pyi', 'exceptions/too_many_requests_error.pyi', 'exceptions/unexpected_error.pyi', 'exceptions/upgrade_required_error.pyi', 'facilitated_details.pyi', 'facilitator_details.pyi', 'granted_payment_instrument_update.pyi', 'iban_bank_account.pyi', 'ids_search.pyi', 'local_payment.pyi', 'local_payment_completed.pyi', 'local_payment_reversed.pyi', 'masterpass_card.pyi', 'merchant.pyi', 'merchant_account/__init__.pyi', 'merchant_account/address_details.pyi', 'merchant_account/business_details.pyi', 'merchant_account/funding_details.pyi', 'merchant_account/individual_details.pyi', 'merchant_account/merchant_account.pyi', 'merchant_account_gateway.pyi', 'merchant_gateway.pyi', 'modification.pyi', 'oauth_access_revocation.pyi', 'oauth_credentials.pyi', 'oauth_gateway.pyi', 'paginated_collection.pyi', 'paginated_result.pyi', 'partner_merchant.pyi', 'payment_instrument_type.pyi', 'payment_method.pyi', 'payment_method_gateway.pyi', 'payment_method_nonce.pyi', 'payment_method_nonce_gateway.pyi', 'payment_method_parser.pyi', 'paypal_account.pyi', 'paypal_account_gateway.pyi', 'paypal_here.pyi', 'plan.pyi', 'plan_gateway.pyi', 'processor_response_types.pyi', 'resource.pyi', 'resource_collection.pyi', 'revoked_payment_method_metadata.pyi', 'risk_data.pyi', 'samsung_pay_card.pyi', 'search.pyi', 'settlement_batch_summary.pyi', 'settlement_batch_summary_gateway.pyi', 'signature_service.pyi', 'status_event.pyi', 'subscription.pyi', 'subscription_details.pyi', 'subscription_gateway.pyi', 'subscription_search.pyi', 'subscription_status_event.pyi', 'successful_result.pyi', 'testing_gateway.pyi', 'three_d_secure_info.pyi', 'transaction.pyi', 'transaction_amounts.pyi', 'transaction_details.pyi', 'transaction_gateway.pyi', 'transaction_line_item.pyi', 'transaction_line_item_gateway.pyi', 'transaction_search.pyi', 'unknown_payment_method.pyi', 'us_bank_account.pyi', 'us_bank_account_gateway.pyi', 'us_bank_account_verification.pyi', 'us_bank_account_verification_gateway.pyi', 'us_bank_account_verification_search.pyi', 'util/__init__.pyi', 'util/constants.pyi', 'util/crypto.pyi', 'util/datetime_parser.pyi', 'util/generator.pyi', 'util/graphql_client.pyi', 'util/http.pyi', 'util/parser.pyi', 'util/xml_util.pyi', 'validation_error.pyi', 'validation_error_collection.pyi', 'venmo_account.pyi', 'version.pyi', 'visa_checkout_card.pyi', 'webhook_notification.pyi', 'webhook_notification_gateway.pyi', 'webhook_testing.pyi', 'webhook_testing_gateway.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
