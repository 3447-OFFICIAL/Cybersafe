from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from main.services.search_service import search_engine
from main.models import CyberCrime

class SearchAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = []

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        
        # If no query, return all
        if not query:
            crimes = list(CyberCrime.objects.all().order_by('-created_at')[:20])
            related_domains = []
        else:
            search_results = search_engine.search(query, top_k=20)
            crime_ids = [res['id'] for res in search_results]
            
            # Fetch objects and preserve ordering by score
            crimes_qs = CyberCrime.objects.filter(id__in=crime_ids)
            crimes_dict = {crime.id: crime for crime in crimes_qs}
            crimes = [crimes_dict[cid] for cid in crime_ids if cid in crimes_dict]
            
            related_domains_set = set()
            for crime in crimes:
                if isinstance(crime.related_domains, list):
                    for domain in crime.related_domains:
                        related_domains_set.add(domain)
            related_domains = list(related_domains_set)[:8]
            
        results = []
        for crime in crimes:
            results.append({
                'id': str(crime.id),
                'type': crime.type,
                'description': crime.description[:150] + '...' if len(crime.description) > 150 else crime.description,
                'category': crime.get_category_display() if hasattr(crime, 'get_category_display') else crime.category,
                'severity': crime.severity,
                'tags': crime.tags if isinstance(crime.tags, list) else [],
                'related_domains': crime.related_domains if isinstance(crime.related_domains, list) else [],
                'prevention_tips': crime.get_prevention_tips_list() if hasattr(crime, 'get_prevention_tips_list') else [],
                'learn_more_clicks': crime.learn_more_clicks
            })
            
        return Response({
            'results': results,
            'related_domains': related_domains
        })

class RelatedThreatsAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = []

    def get(self, request, *args, **kwargs):
        crime_id = request.GET.get('crime_id')
        if not crime_id:
            return Response({'results': []})
            
        search_results = search_engine.get_related_crimes(crime_id, top_k=3)
        crime_ids = [res['id'] for res in search_results]
        
        crimes_qs = CyberCrime.objects.filter(id__in=crime_ids)
        crimes_dict = {crime.id: crime for crime in crimes_qs}
        crimes = [crimes_dict[cid] for cid in crime_ids if cid in crimes_dict]
        
        results = []
        for crime in crimes:
            results.append({
                'id': str(crime.id),
                'type': crime.type,
                'description': crime.description[:100] + '...',
                'category': crime.get_category_display() if hasattr(crime, 'get_category_display') else crime.category,
                'severity': crime.severity,
                'tags': crime.tags if isinstance(crime.tags, list) else []
            })
            
        return Response({'results': results})
