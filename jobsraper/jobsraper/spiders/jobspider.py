import scrapy

class JobspiderSpider(scrapy.Spider):
    name = "jobspider"
    allowed_domains = ["topdev.vn"]
    start_urls = ["https://topdev.vn"]

    def parse(self, response):
        jobs = response.css('div.CardJobList.card-link.block.rounded.border.border-solid.bg-white.p-4')
           
        for job in jobs:
         
            job_texts = job.css('.line-clamp-1 a.whitespace-nowrap.rounded ::text').getall()
            cleaned_job_texts = [text.strip() for text in job_texts]
            
         
            job_hrefs = job.css('.line-clamp-1 a.whitespace-nowrap.rounded::attr(href)').getall()
            
      
            combined_data = list(zip(cleaned_job_texts, job_hrefs))
            
        
            relative_url = job.css('h3 a::attr(href)').get() 
            
        
            jobsdetails_url = response.urljoin(relative_url)  
            
            # Yield thông tin công việc
            # yield {
            #     'job_title': job.css('h3 a::text').get().strip() if job.css('h3 a::text').get() else None,
            #     'Company_name': job.css('.line-clamp-1 a.text-sm.text-gray-500::text').get().strip() if job.css('.line-clamp-1 a.text-sm.text-gray-500::text').get() else None,
            #     'url': jobsdetails_url,
            #     'skills': cleaned_job_texts,
            #     'url_skills': job_hrefs,
            #     'skill_url_pairs': combined_data,
            # }
            
            # Gọi đến trang chi tiết công việc để thu thập thêm thông tin nếu cần
            yield response.follow(jobsdetails_url, callback=self.parse_job_page)

    def parse_job_page(self, response):
        # Lấy và làm sạch văn bản liên quan đến công việc
        texts = response.css('div.flex.w-11\\/12.items-center.text-base.text-gray-500::text').getall()
        cleaned_texts = [text.strip() for text in texts if text.strip()]  
        result = ' '.join(cleaned_texts)
        
      
        links = response.css('a.text-sm.hover\\:text-primary-300::text').getall()
        hrefs = response.xpath('//a[contains(@class, "text-sm")]/@href').getall()
        hrefsJobs = response.css('a.mr-2.inline-block::attr(href)').getall()

      
        if len(links) > 2:
            filtered_data = links[3:6]
            filtered_experience = links[2] if len(links) > 2 else None
            experience = filtered_experience.strip() if filtered_experience else None
        else:
            filtered_data = []
            experience = None
        
      
        for url in hrefsJobs:
            details_url = response.urljoin(url)
            yield response.follow(details_url, callback=self.list_Jobs_page)

   
        yield {
            'job_title': response.css('h1.text-2xl::text').get(),
            'Company_name': response.css('p.my-1.line-clamp-1::text').get(),
            'location': response.css('div.w-11\\/12::text').get().strip() if response.css('div.w-11\\/12::text').get() else None,
            'post': result,
            'salary': response.xpath('//p[contains(@class, "text-primary")]/text()').get(),
            'level': filtered_data,
            'experience': experience,
            'skills': response.css('a.mr-2.inline-block span::text').getall(),
        }

    def list_Jobs_page(self, response):
   
        jobs = response.css('li.mb-4.last\\:mb-0')
       
        for job in jobs:
            relative_url = job.css('h3 a::attr(href)').get()
            jobsdetails_url = response.urljoin(relative_url)
            yield {
                'job_title': job.css('h3.line-clamp-1 a::text').get(),
                'Company_name': job.css('div.mt-1.line-clamp-1 a::text').get(),
                'url': jobsdetails_url,
                'level': job.css('p.text-gray-500::text').getall(),
                'salary': job.css('div.text-primary p::text').get(),
                'location': job.css('div.flex.flex-wrap.items-end p::text').get(),
                'description': job.css('li p.line-clamp-1::text').getall(),
                'skills': job.css('div.line-clamp-1 a.mr-2.inline-block span::text').getall(),
            }
