import random
import string

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
# PDF GENERATION
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, View
from user.models import UserProfile

from .forms import CheckoutForm, CouponForm, PaymentForm, RefundForm
from .models import (Address, Coupon, Order, OrderItem, Payment, Refund,
                     SeedProduct)
from .utils import render_to_pdf

stripe.api_key = settings.STRIPE_SECRET_KEY

User = get_user_model()


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


@method_decorator(login_required, name='dispatch')
class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if order.items.all().count() == 0:
                raise ObjectDoesNotExist
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})

            return render(self.request, "store/checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("store:store")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:

                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('store:checkout')
                else:

                    shipping_street_address = form.cleaned_data.get(
                        'shipping_street_address')
                    shipping_city = form.cleaned_data.get(
                        'shipping_city')
                    shipping_district = form.cleaned_data.get(
                        'shipping_district')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    first_name = form.cleaned_data.get(
                        'first_name')
                    last_name = form.cleaned_data.get(
                        'last_name')
                    # shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([first_name, last_name, shipping_street_address, shipping_country, shipping_city,
                                      shipping_district]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_street_address,
                            city=shipping_city,
                            district=shipping_district,
                            country=shipping_country,
                            address_type='S',
                            first_name=first_name,
                            last_name=last_name
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")
                        return redirect('store:checkout')

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')

                if use_default_billing:
                    print("Using the defualt billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('store:checkout')
                else:
                    billing_street_address = form.cleaned_data.get(
                        'billing_street_address')
                    billing_city = form.cleaned_data.get(
                        'billing_city')
                    billing_district = form.cleaned_data.get(
                        'billing_district')
                    address_email = form.cleaned_data.get(
                        'email')

                    #

                    if is_valid_form([billing_street_address, billing_city, billing_district, address_email]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_street_address,
                            city=billing_city,
                            district=billing_district,
                            secondary_email=address_email,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('store:payment', payment_option='stripe')
                elif payment_option == 'M':
                    return redirect('store:payment', payment_option='momopay')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('store:checkout')
            else:
                messages.info(self.request, 'Fill out the form to proceed')
                return redirect('store:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("store:order-summary")


@method_decorator(login_required, name='dispatch')
class PaymentView(View):
    def get(self, *args, **kwargs):
        payment_option = kwargs['payment_option']
        if payment_option == 'stripe':
            messages.error(
                self.request, 'Sorry, we do not accept payment with stripe yet.')
            return redirect('home')
            # order = Order.objects.get(user=self.request.user, ordered=False)
            # if order.shipping_address:
            #     context = {
            #         'order': order,
            #         'DISPLAY_COUPON_FORM': False,
            #         'publishable_key': settings.STRIPE_PUBLISHABLE_KEY
            #     }
            #     userprofile = self.request.user.userprofile
            #     if userprofile.one_click_purchasing:
            #         # fetch the users card list
            #         cards = stripe.Customer.list_sources(
            #             userprofile.stripe_customer_id,
            #             limit=3,
            #             object='card'
            #         )
            #         card_list = cards['data']
            #         if len(card_list) > 0:
            #             # update the context with the default card
            #             context.update({
            #                 'card': card_list[0]
            #             })
            #     return render(self.request, "store/payment.html", context)
            # else:
            #     messages.warning(
            #         self.request, "You have not added a shipping address")
            #     return redirect("store:checkout")
        elif payment_option == 'momopay':
            messages.error(
                self.request, 'Sorry, we do not accept MOMO PAY yet.')
            return redirect('home')

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)
        if self.request.method == 'POST':
            token = self.request.POST.get('stripeToken')
            save = self.request.POST.get('save')
            use_default = self.request.POST.get('use_default')

            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

            amount = int(order.get_total() * 100 / 924)

            try:

                if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        customer=userprofile.stripe_customer_id
                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        source=token
                    )

                # create the payment
                payment = Payment()
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                # assign the payment to the order

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()

                messages.success(self.request, "Your order was successful!")

                return HttpResponse(f'<h1>Your Order {order.ref_code} is being processed</h1>')
            except:
                return HttpResponse("Error happened")
        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")


class HomeView(ListView):
    model = SeedProduct
    paginate_by = 10
    template_name = "store/store.html"
    context_object_name = 'tree_seeds'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        # context['recent'] = SeedProduct.objects.filter(available=True).order_by('-created_on')[:10]

        return context


@method_decorator(login_required, name='dispatch')
class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'store/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("store:store")


class SeedProductDetailView(DetailView):
    model = SeedProduct
    template_name = "store/product.html"
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super(SeedProductDetailView, self).get_context_data(**kwargs)
        context['related'] = SeedProduct.objects.filter(available=True)
        context['new_products'] = SeedProduct.objects.filter(
            available=True).order_by('-created_on')[:5]
        return context


@login_required
def add_to_cart(request, slug):
    get_quantity = request.GET.get('quantity')
    try:
        quantity = float(get_quantity)
    except TypeError as e:
        quantity = 1
    item = get_object_or_404(SeedProduct, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            if order_item.quantity >= 9:
                messages.error(
                    request, 'Maximum allowed order quantity is 9 Kg')
                return redirect("store:order-summary")
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Item quantity was updated.")
            return redirect("store:order-summary")
        else:
            order_item.quantity = quantity
            order_item.save()
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("store:order-summary")
    else:
        order_item.quantity = quantity
        order_item.save()
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.success(request, "Item added to your cart.")
        return redirect("store:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(SeedProduct, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("store:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("store:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("store:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(SeedProduct, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("store:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("store:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("store:product", slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("store:checkout")


@method_decorator(login_required, name='dispatch')
class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("store:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("store:checkout")


@method_decorator(login_required, name='dispatch')
class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("store:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("store:request-refund")


def generate_card(request, slug):
    item = get_object_or_404(SeedProduct, slug=slug)
    if item:
        context = {'item': item}
        return render(request, 'store/card.html', context)
    else:
        return redirect("store:order-summary")


def download_pdf(request, slug):
    item = get_object_or_404(SeedProduct, slug=slug)
    if item:
        context = {
            'item': item
        }
        file_name = '%s-%s' % (item.scientific_name, item.id)
        template_name = 'store/card_pdf.html'
        return render_to_pdf(template_name, context)
    else:
        messages.info(request, 'This product does not exist')
        return redirect('home')


@login_required
def delete_product(request, pk):
    product = SeedProduct.objects.get(id=pk)
    name = product.scientific_name

    product.available = False
    product.save()

    messages.info(request, '{} - Was deleted from your database'.format(name))
    return redirect('product')


def order_detail(request, pk):
    order = get_object_or_404(Order, id=pk)
    if order:
        order_exist = True
        order_items = order.items.all()
        all_items = []
        for item in order_items:
            item_name = '%s X %s (%s)' % (
                item.quantity, item.item.scientific_name, item.get_final_price())
            all_items.append(item_name)
        # all_items = serializers.serialize("json", order_items)
        total = order.get_total()
        cancel_url = str(order.cancel_url())
        data = {
            'items': all_items,
            'total': total,
            'id': order.id,
            'cancel': cancel_url
        }
        return JsonResponse(data)
    else:
        order_exist = False

        data = {
            'id': 1,
            'items': 3,
            'order': order_exist,
        }
        return JsonResponse(data)


def cancel_order(request, pk):
    order = get_object_or_404(Order, id=pk)
    if order:
        if order.payment is not None and not order.received:
            messages.warning(request, 'You can not cancel an active order')
            return redirect('orders')
        elif order.refund_requested and not order.refund_granted:
            messages.error(request, 'Wait for refund processing')
            return redirect('orders')
        elif order.being_delivered and not order.received:
            messages.error(request, 'Wait for order completion')
            return redirect('orders')
        else:
            order.ordered = False
            order_reference = order.ref_code
            order.delete()
            messages.success(
                request, f'Order with ref code {order_reference} has been cancelled and deleted')
            return redirect('orders')


def order_received_view(request, pk):
    pass


def request_refund_view(request, pk):
    pass


def update_item_cart_quantity(request):
    pk = request.GET.get('pk')
    q = request.GET.get('q')
    item = get_object_or_404(OrderItem, pk=pk)

    if item:
        item.quantity = q
        item.save()
        data = {'message': 'Item exist',
                'quantity': item.quantity}

        return JsonResponse(data)
